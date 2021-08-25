import argparse
import io
import logging
from typing import Any, Mapping, Tuple

import PIL
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Model
from django.utils import timezone
from django.utils.functional import cached_property

from importo.models import APIHashMixin
from importo.readers.base import BaseReader
from importo.readers.csv import SimpleCSVReader
from importo.utils.files import fetch_file, filename_from_url, static_file_to_bytesio
from importo.utils.values import extract_row_value

VERBOSITY_TO_LOGGING_LEVEL = {
    1: logging.ERROR,
    2: logging.INFO,
    3: logging.DEBUG,
}

FILE_TYPE_IMAGE = "image"
FILE_TYPE_AUDIO = "audio"
FILE_TYPE_DOCUMENT = "document"
FILE_TYPE_VIDEO = "video"

DUMMY_IMAGE_PATH = "importo/dummy_files/dummy.png"
DUMMY_DOCUMENT_PATH = "importo/dummy_files/dummy.pdf"


class BaseImportCommand(BaseCommand):
    target_model = None
    source_id_field = ""
    target_model_id_field = ""

    # Contents should follow the format:
    # (source_name, model_field_name, fallback)
    import_fields = []

    reader_class = SimpleCSVReader

    # Set this when using a database powered reader to avoid having to specify
    # every time you use the command
    default_source_db = None

    def add_arguments(self, parser):
        if self.reader_class.requires_file_input:
            parser.add_argument(
                "file",
                required=True,
                type=argparse.FileType("r"),
                help=self.reader_class.file_input_help,
            )

        if self.reader_class.requires_db_connection:
            common_kwargs = dict(
                type=str,
                choices=tuple(settings.DATABASES.keys()),
                help=self.reader_class.db_connection_help,
            )
            if not self.default_source_db:
                parser.add_argument("db", required=True, **common_kwargs)
            else:
                parser.add_argument("--db", "-d", **common_kwargs)

        parser.add_argument(
            "--start-row",
            type=int,
            help=(
                "Optionally specify the row number to start operating on, "
                "skipping over any preceeding rows. Applies to the first "
                "processed page only. Most useful when combined with "
                "'--page' or '--start-page' to restart an import at the "
                "point where it last failed."
            ),
        )
        parser.add_argument(
            "--stop-row",
            type=int,
            help=(
                "Optionally specify the row number to stop operating on for "
                "all pages. Most useful when combined with '--page' and "
                "'--start-row' to target a range of rows to operate on."
            ),
        )

        if self.reader_class.supports_pagination:
            parser.add_argument(
                "--page",
                type=int,
                help=(
                    "Optionally specify a single page of source data to operate "
                    "on. Useful during development to test the process "
                    "on a smaller dataset. When provided, overrides both "
                    "the 'start-page' and 'end-page' option values."
                ),
            )
            parser.add_argument(
                "--start-page",
                type=int,
                help=(
                    "Optionally specify a page of source data to start operating on, "
                    "skipping over any preceeding pages."
                ),
            )
            parser.add_argument(
                "--stop-page",
                type=int,
                help=(
                    "Optionally specify the last page of source data to operate on. "
                    "The import will stop once this page has been processed."
                ),
            )
            parser.add_argument(
                "--pagesize",
                type=int,
                help=(
                    "Optionally override the number of rows that are fetched from "
                    "the data source at any one time. If not specified, a default "
                    "value will be used (which will differ between imports). "
                    "WARNING: The higher the number, the more memory-hungry the "
                    "process will be."
                ),
            )

        if self.reader_class.supports_throttling:
            parser.add_argument(
                "--throttle",
                type=float,
                help=(
                    "Number of seconds to wait between fetching a new page of "
                    "results from the data source. Set this high to avoid "
                    "hammering an API over an extended period of time. If not "
                    "specified, a default value will be used (which will differ "
                    "between imports)."
                ),
            )

        parser.add_argument(
            "--resilient",
            "-r",
            action="store_true",
            help=("Log known errors, but do not allow them to hault the process."),
        )

        parser.add_argument(
            "--force-update",
            "-f",
            action="store_true",
            help=(
                "Process rows even if skip_update() returns False. Useful "
                "for re-running updated/in-development imports, where you "
                "want rows to processed regardless."
            ),
        )

        parser.add_argument(
            "--dryrun",
            action="store_true",
            help=("Run the import without saving any changes to the database."),
        )

        parser.add_argument(
            "--novalidate",
            action="store_true",
            help=(
                "Do not use the target model's built-in clean methods to "
                "validate instances before attempting to save changes."
            ),
        )

        parser.add_argument(
            "--mock-downloads",
            action="store_true",
            help="Use placeholders for file downloads instead of downloading from source (used for testing)",
        )

    def execute(self, *args, **options):
        self.setup(options)
        return super().execute(*args, **options)

    def handle(self, **options) -> None:
        for row in self.reader:
            self.sanitize_row(row)
            self.process_row(row)

        self.logger.info("That's all folks!")

    def setup(self, options):
        self.verbosity = int(options.get("verbosity", 2))
        for key, value in options.items():
            setattr(self, key, value)
        self.logger = self.create_logger(self.verbosity)
        self.reader = self.create_reader(options)

    def create_logger(self, verbosity: int):
        logger = logging.getLogger(self.__class__.__module__)
        logger.propagate = False

        # Only log feedback that is of interest
        logger.setLevel(VERBOSITY_TO_LOGGING_LEVEL.get(verbosity, logging.ERROR))

        # Add a new line after everything that is logged
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s\n"))
        logger.handlers = [handler]
        return logger

    def create_reader(self, options: Mapping[str, Any]) -> BaseReader:
        kwargs = self.get_reader_kwargs(options)
        return self.reader_class(self.logger, **kwargs)

    def get_reader_kwargs(self, options: Mapping[str, Any]) -> Mapping[str, Any]:
        kwargs = {}
        if self.reader_class.requires_file_input:
            kwargs["file"] = options["file"]
        if self.reader_class.requires_db_connection:
            kwargs["db"] = options.get("db") or self.default_source_db
        kwargs = {
            "start_row": options.get("start_row"),
            "stop_row": options.get("stop_row"),
        }
        if self.supports_pagination:
            kwargs.update(
                start_page=options.get("page") or options.get("start_page"),
                stop_page=options.get("page") or options.get("stop_page"),
                page_size=options.get("pagesize"),
            )
        if self.supports_throttling:
            kwargs["throttle"] = options.get("throttle")
        return kwargs

    @property
    def current_row_number(self):
        return self.reader.current_row_number

    @property
    def current_row_data(self):
        return self.reader.current_row_data

    def get_queryset(self):
        return self.target_model.objects.all()

    @cached_property
    def source_ids_from_db(self):
        return set(
            self.get_queryset().values_list(self.target_model_id_field, flat=True)
        )

    def sanitize_row(self, data: Any) -> None:
        """
        This method is called for every row before `data` is passed to `process_row()`
        for processing. It should manipulate `data` in-place, and doesn't need to
        return anything. No changes are applied by default. It is the responsibility of
        each subclasses to apply additional sanitization where required.
        """
        pass

    def process_row(self, data: Any) -> None:
        """
        This method is responsible for deciding what to do with the data for a
        given row. It's unlikely that you'll need to override this method.
        """
        obj, is_new = self.get_or_initialise_object(data)
        self.current_object = obj

        if self.skip_update(obj, data, is_new):
            self.logger.info("Skipping update for object.")
            return

        self.update_object(obj, data, is_new)
        if self.conditionally_validate_object(obj, is_new):
            self.conditionally_save_object(obj, is_new)

    def get_or_initialise_object(self, data: Any) -> Tuple[Model, bool]:
        """
        Returns an instance of `self.target_model` with an ID matching that
        found in the source data. If a match cannot be found in the database,
        a new/unsaved instance will be returned, with the relevant ID field
        value set.
        """
        target_model = self.get_target_model(data)
        source_id = self.get_source_id(data)
        if source_id in self.source_ids_from_db:
            try:
                obj = self.get_object(source_id, target_model)
                self.logger.info(
                    f"Found existing {target_model._meta.verbose_name} to update: {obj}."
                )
                return obj, False
            except target_model.DoesNotExist:
                pass
        self.logger.info(f"Creating new {target_model._meta.verbose_name}.")
        return self.initialise_object(source_id, data, target_model), True

    def get_object(self, source_id: Any, target_model: type) -> Model:
        """
        Returns an instance of ``self.target_model`` matching the provided
        ``source_id``. Should raise `self.target_model.DoesNotExist` if no
        matching instance can be found.
        """
        lookups = {self.target_model_id_field: source_id}
        return self.get_queryset().get(**lookups)

    def get_init_kwargs(self, source_id, data: Any, target_model: type) -> dict:
        """
        Returns a ``dict`` of values for initialise_object()
        to use when initialising a new object.
        """
        return {self.target_model_id_field: source_id}

    def initialise_object(self, source_id, data: Any, target_model: type) -> Model:
        """
        Returns a new, unsaved instance of ``self.target_model``
        ready to be updated by update_object().
        """
        return target_model(**self.get_init_kwargs(source_id, data, target_model))

    def skip_update(self, obj: Model, data: Any, is_new: bool) -> bool:
        """
        Override to skip updating, validation and saving for the supplied
        ``obj``. For example, if it doesn't look like things have changed
        since the last update.

        If the target model is a subclass of APIHashMixin, the import will
        automatically attempt to compare a hash of the new representation
        with the one stored on the model to figure out if anything has changed.
        """
        if issubclass(self.target_model, APIHashMixin):
            current_hash = obj.api_hash
            try:
                new_hash = obj.get_hash(data)
            except Exception:
                if self.resilient_mode:
                    self.logger.exception("Error hashing new row data.")
                    return False
                else:
                    raise
            else:
                # Always set the api_hash value to the latest representation
                obj.api_hash = new_hash
                if not self.force_update and not is_new and current_hash == new_hash:
                    return True
        return False

    def update_object(self, obj: Model, data: Any, is_new: bool) -> None:
        """
        Update the supplied ``obj`` according to the values in
        ``data``. By default, the keys/attributes specified in
        ``import_fields`` are used to find new values.
        """
        obj.last_imported_at = timezone.now()
        for key, field_name, fallback in self.import_fields:
            value = extract_row_value(key, data, fallback)
            setattr(obj, field_name, value)

    def conditionally_validate_object(self, obj: Model, is_new: bool) -> bool:
        if self.novalidate:
            return True

        self.logger.info("Validating object.")
        try:
            self.validate_object(obj, is_new)
            return True
        except ValidationError:
            if self.resilient_mode:
                self.logger.exception("Validation failure")
                return False
            else:
                raise

    def validate_object(self, obj: Model, is_new: bool) -> None:
        obj.full_clean()

    def conditionally_save_object(self, obj: Model, is_new: bool) -> None:
        if self.dryrun:
            return

        self.logger.info("Saving object.")
        try:
            self.save_object(obj, is_new)
            return
        except (IntegrityError, ValidationError):
            if self.resilient_mode:
                self.logger.exception("Save failure")
            else:
                raise

    def save_object(self, obj: Model, is_new: bool) -> None:
        obj.save()

    def get_source_id(self, data: dict):
        """
        Return a value from the supplied row data that can be used to
        """
        return extract_row_value(self.source_id_field, data)

    def get_target_model(self, data: Any) -> type:
        return self.target_model

    def get_file_from_url(self, file_url: str, file_type: str):
        if self.mock_downloads:
            self.logger.debug(f"Using placholder {file_type} for: {file_url}")
            file = self.get_placeholder_file(file_type)
            file.seek(0)
        else:
            self.logger.debug(f"Fetching file: {file_url}")
            try:
                return fetch_file(file_url)
            except Exception:
                self.logger.exception("Error fetching file from: {file_url}")
                return None

        # Validate downloaded images
        if not self.mock_downloads and file_type == FILE_TYPE_IMAGE:
            tmp_image = PIL.Image.open(file)
            file.seek(0)
            try:
                tmp_image.verify()
            except Exception:
                self.logger.exception("Error validating image: {file_url}")
                return None

        filename = filename_from_url(file_url)
        if self.mock_downloads:
            # If the import is repeated with real file downloads, we don't want
            # filenames to have to be suffixed because of clashes.
            filename = f"dummy__{filename}"

        return SimpleUploadedFile(filename, file.getvalue())

    def get_placeholder_file(self, file_type: str) -> io.BytesIO:
        if file_type == FILE_TYPE_IMAGE:
            return self.placeholder_image
        if file_type == FILE_TYPE_DOCUMENT:
            return self.placeholder_document
        if file_type == FILE_TYPE_AUDIO:
            return self.placeholder_audio
        if file_type == FILE_TYPE_VIDEO:
            return self.placeholder_video
        return io.BytesIO()

    @cached_property
    def placeholder_image(self) -> io.BytesIO:
        return static_file_to_bytesio(DUMMY_IMAGE_PATH)

    @cached_property
    def placeholder_document(self) -> io.BytesIO:
        return static_file_to_bytesio(DUMMY_DOCUMENT_PATH)

    @cached_property
    def placeholder_audio(self) -> io.BytesIO:
        """
        Override this method to return a more realistic file to
        use as audio. By default, an empty file is returned.
        """
        return io.BytesIO()

    @cached_property
    def placeholder_video(self) -> io.BytesIO:
        """
        Override this method to return a more realistic file to
        use as video. By default, an empty file is returned.
        """
        return io.BytesIO()
