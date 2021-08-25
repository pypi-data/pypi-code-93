from os import walk
from sys import stderr
from itertools import chain
from pathlib import Path
from enum import Enum
from ...scan.io import mmd
from functools import partial
from .html_page_util import HtmlDoc, HtmlPage
from .html_util import Attrs, PartialAttrs, CustomHtmlTag
from .html_index_util import EmittedIndex, IntermedDirIndex, WireIndex
from .sinks import DocSink
from ..yaml_util import get_yaml_manifest
from ...__share__ import alphanum2num_monthdict
from bs4 import Tag

__all__ = ["BaseEmitter", "Emitter"]

class BaseEmitter:
    """
    The minimum viable task of an emitter is to take a directory of MMD documents
    and transform it into a corresponding HTML output.

    The first built on top of this is `WireEmitter`, which uses a `wire.mmt` file
    to specify which files in the directory will be emitted (not necessary if all
    will be).
    """
    @property
    def doc_subpaths(self):
        "Probably doesn't work/don't need (to be deleted...)"
        return [x.src_filepath.relative_to(self.dir) for x in self.docs]

def match_date_parts(path_parts):
    for i, p in enumerate(path_parts):
        if i == 0 or i >= len(path_parts) - 1:
            continue # skip first and last parts for indexing trios
        if p in alphanum2num_monthdict:
            p_pre, p_post = path_parts[i-1], path_parts[i+1]
            if p_pre.isnumeric() and p_post.isnumeric():
                numeric_month = str(alphanum2num_monthdict.get(p))
                return p_pre, numeric_month, p_post
    raise ValueError(f"No alphanumeric month-containing date found in '{path_parts}'")

class Wire:
    """
    `Wire` objects are created as `WireEmitter._Wires` in a listcomp
    within the method `WireEmitter.procure_documents`.
    """
    def __init__(self, filepath, verbose=False):
        self.date = match_date_parts(filepath.parts)
        self.source = mmd(filepath)
        self.source_dir = filepath.parent
        self.sinks = []
        for b in self.source.blocks:
            # TODO: add a lever parsing class rather than manually doing this
            d = dict([map(str.strip, n.contents.split("⠶")) for n in b.nodes])
            source_files = d.get("transmit").split(",")
            template = d.get("template")
            # Enum wrapper to template class: select the class from template string
            sink_func = getattr(DocSink, template).value
            # positional arg partial func: different files share same source directory
            make_sink = partial(sink_func, self.date, self.source_dir, verbose=verbose)
            templated_sinks = list(map(make_sink, source_files))
            self.sinks.extend(templated_sinks)

class WireEmitter(BaseEmitter):
    """
    The `.sink`s on the `._Wire`s are the `.docs`, emitted upon `._trigger()`.
    """
    def __init__(self, directory, name, verbose=False):
        self._verbose = verbose
        if self._verbose:
            print(f"== WireEmitter: '{name}'==", file=stderr)
        self.dir = directory
        subdir = get_yaml_manifest("poll").pages.script.cfg.get("subdirectory") # site
        self.target_dir = (self.dir / "..").resolve() / subdir / "wire"
        self.name = name
        self._procure_documents() # populate the docs property via wire files
        self.emit_log = [] # populated for the first time upon trigger 
        self._trigger()
        if self._verbose:
            print("Emit log: \n  " + "\n  ".join([str(x) for x in self.emit_log]), file=stderr)
        self._index_emissions()

    def _procure_documents(self):
        walker = walk(self.dir)
        wire = "wire.mmt"
        dirs = [Path(p) for (p, _, filenames) in walker if wire in filenames]
        if self._verbose:
            print("TARGET DIR ::", self.target_dir, file=stderr)
            print("All input wire dirs:", file=stderr)
            for p in dirs:
                print("  " + str(p), file=stderr)
        self.wires = [(p / wire) for p in dirs]
        self._Wires = [Wire(w, verbose=self._verbose) for w in self.wires]
        self.docs = list(chain.from_iterable([w.sinks for w in self._Wires]))

    def _trigger(self):
        # put the files in the new directory
        emitted_paths = []
        for d in self.docs:
            # write output to target in the target directory
            emitted_path = d.emit(self.target_dir)
            emitted_paths.append(emitted_path)
        self.emit_log.extend(emitted_paths) # set as empty list in __init__

    def _index_emissions(self):
        lambda_sort = lambda x: [int(str(p)) if str(p).isnumeric() else str(p) for p in x.parts]
        all_emission_dirs = sorted(set([p.parent for p in self.emit_log]), key=lambda_sort)
        if self._verbose:
            print("Emit dirs:\n  " + "\n  ".join([str(x) for x in all_emission_dirs]), file=stderr)
        rel_dirs = [d.relative_to(self.target_dir) for d in all_emission_dirs]
        if self._verbose:
            print("All wire emitted dirs:\n  " + "\n  ".join([f"{d}" for d in rel_dirs]))
        all_subdirs = [[d] + [x for x in d.parents if x.parts] for d in rel_dirs]
        unique_subdirs = [] # didn't feel like using a set
        for l in all_subdirs:
            for d in l:
                if d in unique_subdirs:
                    continue
                unique_subdirs.append(d)
        if self._verbose:
            print("unique subdirs: \n  " + "\n  ".join([f"{s}" for s in sorted(unique_subdirs)]))
        su_subdirs = sorted(unique_subdirs)
        top_level_subdirs = [d for d in sorted(unique_subdirs) if len(d.parts) == 1]
        self._index_emission_dir(Path("."), top_level_subdirs)
        for d in su_subdirs:
            self._index_emission_dir(d, unique_subdirs)

    def _index_emission_dir(self, e_dir, all_subdirs):
        f_name = "index.html"
        full_e_dir = self.target_dir / e_dir
        p = full_e_dir / f_name
        if len(e_dir.parts) == 0: # i.e. the top-level path "."
            files_to_log = []
        else:
            files_to_log = [e for e in self.emit_log if e.parent == full_e_dir]
            names_to_log = [p.relative_to(full_e_dir) for p in files_to_log]
        if self._verbose:
            print(f"  ⇢ index files: {e_dir}")
        if files_to_log:
            # i.e. if there are direct file descendants of the directory (not just subdirs)
            index_html_file = EmittedIndex(names_to_log, e_dir).as_str()
            n_f = len(files_to_log)
            f_str = f"{n_f} file{'s' if n_f != 1 else ''}"
            if self._verbose:
                print(f"    Writing index of {f_str} at {p}")
        else:
            if len(e_dir.parts) == 0: # i.e. the top-level path "."
                subdirs = all_subdirs
                index_html_file = WireIndex(subdirs, e_dir).as_str()
            else:
                subdirs = [d.relative_to(e_dir) for d in all_subdirs if d.parent == e_dir]
                index_html_file = IntermedDirIndex(subdirs, e_dir).as_str()
            n_sd = len(subdirs)
            subdir_str = f"{n_sd} subdirector{'ies' if n_sd != 1 else 'y'}"
            if self._verbose:
                print(f"    Writing index of {subdir_str} at {p}")
        with open(p, "w") as f:
            f.write(index_html_file)
        return

class Emitter(Enum):
    wire = WireEmitter
