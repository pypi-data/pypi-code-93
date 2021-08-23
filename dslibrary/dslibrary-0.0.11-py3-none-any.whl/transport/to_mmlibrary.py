"""
Adapter to "mmlibrary".

The "mmlibrary" package can be installed locally to provide a default custom target.
"""
import io
import json
import inspect

from dslibrary.engine_intf import FileSystem
from dslibrary.front import DSLibraryException
from dslibrary.metadata import Metadata
from dslibrary.utils.file_utils import write_stream_with_read_on_close
from dslibrary import DSLibrary

try:
    import mmlibrary
except ImportError:
    mmlibrary = None


class DSLibraryViaMMLibrary(DSLibrary):
    def __init__(self, *args, _mm=None, **kwargs):
        """
        :param _mm:    You can reference a custom set of functions instead of the mmlibrary package.
        """
        self._mm = _mm or mmlibrary
        super(DSLibraryViaMMLibrary, self).__init__(*args, **kwargs)

    def get_metadata(self):
        return Metadata()

    def _find_method(self, *args, mandatory: bool=True):
        """
        Find a method that matches one of the names given in 'args'.
        """
        for method in args:
            if hasattr(self._mm, method):
                return getattr(self._mm, method)
        if mandatory:
            raise DSLibraryException(f"method not found: {args[0]}()")

    def get_parameters(self):
        if not self._mm:
            return {}
        get_arguments = self._find_method("get_arguments", "get_parameters", mandatory=False)
        if get_arguments:
            return self._mm.get_arguments()
        if hasattr(self._mm, "param_dictionary"):
            return self._mm.param_dictionary
        raise DSLibraryException(f"method not found: get_arguments()")

    def get_parameter(self, parameter_name: str, default=None):
        if not self._mm:
            return default
        method = self._find_method("get_parameter", "get_argument", "getArgument")
        try:
            return method(parameter_name)
        except (ValueError, KeyError):
            pass
        return default

    def _opener(self, path: str, mode: str, **kwargs) -> io.IOBase:
        if 'w' in mode:
            writer = self._find_method("save_binary_to_resource", "saveBinaryToResource")
            def finalize(fh):
                writer(path, fh.read())
            return write_stream_with_read_on_close(w_mode=mode, r_mode='rb', on_close=finalize)
        if "r" in mode:
            try:
                reader = self._find_method("get_binary_from_resource", "getBinaryFromResource")
                if mode == 'rb':
                    return io.BytesIO(reader(path))
                return io.StringIO(reader(path).decode('utf-8'))
            except ValueError:
                raise FileNotFoundError(f"not found: {path}")
        raise DSLibraryException(f"Unsupported mode: {mode}")

    def get_filesystem_connection(self, resource_name: str, for_write: bool=False, **kwargs):
        open_method = self._find_method("open_stream")
        if not open_method:
            raise DSLibraryException(f"No filesystem engine access available, requested={resource_name}")
        bucket = kwargs.get("bucket")
        file_source = f"{resource_name}:{bucket}" if bucket else resource_name
        class MMFS(FileSystem):
            def ls(self, path, detail=True, **kwargs):
                raise NotImplementedError()
            def rm(self, path, recursive=False, maxdepth=None):
                raise NotImplementedError()
            def mkdir(self, path, create_parents=True, **kwargs):
                raise NotImplementedError()
            def stat(self, path, **kwargs):
                raise NotImplementedError()
            def open(self, path, mode="rb", block_size=None, cache_options=None, **kwargs):
                return open_method(path, file_source=file_source, mode=mode)
        return MMFS()

    def open_model_binary(self, part: str=None, mode: str='rb') -> io.RawIOBase:
        """
        The model-binary is just one file, but we can support 'part' by assuming it is a ZIP file.
        """
        if part:
            import zipfile
            if mode in ("w", "wb", "a", "ab"):
                # we can't write parts because each call to mmlibrary.new_version() creates a new trained model
                raise ValueError(f"Unsupported mode for model binary with parts: {mode}")
            with self.open_model_binary() as f_r:
                with zipfile.ZipFile(f_r) as zf:
                    if mode == "r":
                        return io.StringIO(zf.read(part).decode("utf-8"))
                    if mode == "rb":
                        return io.BytesIO(zf.read(part))
        if "r" in mode:
            get_model = self._find_method("get_model", "getModel")
            return open(get_model(), mode)
        if "w" in mode:
            wr_model = self._find_method("new_version", "newVersion")
            return write_stream_with_read_on_close(w_mode=mode, r_mode='rb', on_close=lambda f_r: wr_model(f_r.read()))

    def log_metric(self, metric_name: str, metric_value: float, step: int=0) -> None:
        """
        MMlibrary has its own KPI logging method.
        """
        if self._mlflow_metrics:
            return super(DSLibraryViaMMLibrary, self).log_metric(metric_name, metric_value, step)
        self._mm.save_kpi(metric_name, metric_value)

    def open_run_data(self, filename: str, mode: str='rb') -> io.IOBase:
        """
        The method provided by mmlibrary to save 'run data' only stores a single chunk of binary data.  We
        store JSON in that data, and translate calls to read and write files such that they read and write
        elements of that JSON object.
        """
        reader = self._find_method("get_temporary_data")
        if "r" in mode:
            data = json.loads(reader() or b'{}')
            if filename not in data:
                raise FileNotFoundError(f"not found: {filename}")
            if mode == 'r':
                return io.StringIO(data[filename])
            return io.BytesIO((data[filename]).encode("utf-8"))
        def finalize(fh):
            data = json.loads(reader() or b'{}')
            if "a" in mode:
                if filename not in data:
                    data[filename] = ""
                data[filename] += fh.read()
            else:
                data[filename] = fh.read()
            writer = self._find_method("save_temporary_data")
            writer(json.dumps(data).encode('utf-8'))
        return write_stream_with_read_on_close(w_mode=mode, r_mode='r', on_close=finalize)

    def get_next_scoring_request(self, timeout: float=None) -> (dict, None):
        raise DSLibraryException("not implemented in mmlibrary, use get_parameter() for each fields of a single scoring request")

    def scoring_response(self, score):
        method = self._find_method("return_score", "returnScore")
        method(score)

    def get_sql_connection(self, resource_name: str, for_write: bool=False, database: str=None, **kwargs):
        method = self._find_method("get_db_connection", "getDBConnection")
        sig = inspect.signature(method)
        params = {}
        if database:
            if "database" in sig.parameters:
                params["database"] = database
            else:
                raise DSLibraryException("The 'database' parameter is not supported by this implementation of get_db_connection()")
        return method(resource_name, **params)

    def install_packages(self, packages: list, verbose: bool=False):
        method = self._find_method("install_packages")
        sig = inspect.signature(method)
        if method:
            return method(packages)
        else:
            return super(DSLibraryViaMMLibrary, self).install_packages(packages, verbose)
