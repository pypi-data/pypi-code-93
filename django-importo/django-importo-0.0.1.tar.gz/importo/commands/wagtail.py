import argparse
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.utils.functional import cached_property
from wagtail.core.models import Collection, CollectionMember, Page, Site

from importo.utils.values import get_row_value, set_row_value

from .base import BaseImportCommand


class BasePageImportCommand(BaseImportCommand):
    parent_page_type = None
    move_existing_pages = False

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--parent-id", type=int)

    def setup(self, *args, **options):
        super().setup(*args, **options)
        self.parent_id = options.get("parent_id")

    def conditionally_validate_object(self, obj: Model, is_new: bool) -> bool:
        """
        Overrides BaseImportCommand.conditionally_validate_object()
        to prevent validation pages, as it's better for validation
        to be triggered by Page.save() once any values have been
        suitably adjusted.
        """
        return True  # indicate validation success

    def save_object(self, obj: Page, is_new: bool) -> None:
        """
        Overrides BaseImportCommand.save_object() to create revisions, publish,
        unpublish and move pages to the correct part of the page tree.
        """
        if is_new or self.move_existing_pages:
            parent = self.get_parent_page(obj)
        else:
            parent = None

        if is_new:
            # Creating new page
            parent_page = self.get_parent_page(obj)
            try:
                # Using `try` in case saving fails due to
                # validation/other issues
                parent_page.add_child(instance=obj)
            except Exception:
                # Revert unintended in-memory changes to `numchild`
                # so that the import process can continue
                parent_page.refresh_from_db(fields=["numchild"])
                raise
        else:
            if self.move_existing_pages:
                if obj.depth != (parent.depth + 1) or not obj.path.startswith(
                    parent.path
                ):
                    obj.move(parent, "last-child")
            revision = obj.save_revision(changed=False, clean=False)
            if obj.live:
                revision.publish()
            else:
                obj.unpublish()
            return

    def get_parent_page(self, obj: Page):
        return self.default_parent_page

    @cached_property
    def default_parent_page(self):
        """
        Return a page to use as the parent for pages created by this
        import. Imports can override ``get_parent_page()`` to select a
        different parent depending on the page, but most will set
        `parent_page_type` and add pages to the same place in the tree.
        """
        if self.parent_page_type:
            qs = self.parent_page_type.objects.all()
            if self.parent_id:
                return qs.get(id=self.parent_id)
            parent = qs.first()
            if parent is not None:
                return parent
        return Site.objects.get(is_default_site=True).root_page.specific


class BaseCollectionMemberImportCommand(BaseImportCommand):
    target_collection_name = None
    target_collection_id = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--target-collection-id", type=int)

    def setup(self, *args, **options):
        super().setup(*args, **options)
        if collection_id := options.get("target_collection_id"):
            self.target_collection_id = collection_id

    def get_target_collection(self, obj: CollectionMember):
        return self.default_target_collection

    @cached_property
    def default_target_collection(self):
        if self.default_collection_id:
            return Collection.objects.get(id=self.default_collection_id)
        if self.default_collection_name:
            return Collection.objects.get(name=self.default_collection_name)
        return Collection.get_first_root_node()

    def update_object(self, obj: Model, data: Any, is_new: bool) -> None:
        if is_new:
            obj.collection = self.get_target_collection(obj)
        super().update_object(obj, data, is_new)


class BaseMediaImportCommand(BaseCollectionMemberImportCommand):
    file_type = None
    source_file_url_field = "file"
    target_file_field = "file"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--mock-downloads",
            action="store_true",
            help="Use local dummy files for files instead of downloading from source (for testing).",
        )

    def get_file_type(self):
        if not self.file_type:
            raise ImproperlyConfigured(
                "Subclasses of BaseMediaImportCommand must a 'file_type' attribute value."
            )
        return self.file_type

    def skip_update(self, obj: Model, data: Any, is_new: bool) -> bool:
        # Skip rows with missing file urls
        file_url = get_row_value(data, self.source_file_url_field)
        if file_url:
            return True

        super_result = super().skip_update(obj, data, is_new)
        if super_result:
            return super_result

        # Attempt fetch the file
        file = self.get_file_from_url(file_url, file_type=self.get_file_type())

        # Skip rows where with download issues
        if file is None:
            return True

        # Replace file url with the file
        set_row_value(data, self.source_file_url_field, file)

    def update_object(self, obj: Model, data: Any, is_new: bool) -> None:
        existing_file_value = getattr(obj, self.target_file_field)
        new_file_value = get_row_value(data, self.source_file_url_field)

        # Update remaining field values
        super().update_object(obj, data, is_new)

        if self.mock_downloads:
            if existing_file_value:
                # Avoid replacing existing files with dummy ones
                obj.file = existing_file_value
            else:
                obj.file = new_file_value
                # Avoid the overhead of hashing if mocking downloads
                obj.hash = ""
        else:
            # This should have been set by utils.io.fetch_file()
            new_file_hash = new_file_value.hash
            if is_new or new_file_hash != obj.file_hash:
                obj.file = new_file_value
                obj.file_hash = new_file_hash
