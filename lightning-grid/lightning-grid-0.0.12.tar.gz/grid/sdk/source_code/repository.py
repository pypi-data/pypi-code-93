"""TODO(rlizzo): THIS FILE IS PART OF PROJECT FEYNMAN
"""
from contextlib import contextmanager
import os
from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree
from typing import Optional

import grid.sdk.source_code.gridignore as gridignore
from grid.sdk.source_code.hashing import dirhash
from grid.sdk.utils.tar import tar_path
from grid.sdk.utils.uploader import S3Uploader


class LocalRepository:
    """Utilities for managing local source-code used for creating Runs."""
    cache_location: Path = Path.home() / ".grid" / "cache" / "repositories"

    def __init__(self, path: Path):
        self.path = path

        # cache checksum version
        self._version: Optional[str] = None

        # create global cache location if it doesn't exist
        if not self.cache_location.exists():
            self.cache_location.mkdir(parents=True, exist_ok=True)

        # clean old cache entries
        self._prune_cache()

    @property
    def version(self):
        """
        Calculates the checksum of a local path.

        Parameters
        ----------
        path: Path
            Reference to a path.
        """
        # cache value to prevent doing this over again
        if self._version is not None:
            return self._version

        self._version = dirhash(path=self.path, algorithm="blake2", ignore=gridignore.generate(src=self.path))
        return self._version

    @property
    def package_path(self):
        """Location to tarball in local cache."""
        filename = f"{self.version}.tar.gz"
        return self.cache_location / filename

    @contextmanager
    def packaging_session(self) -> Path:
        """Creates a local directory with source code that is used for creating a local source-code package."""
        try:
            session_path = self.cache_location / "packaging_sessions" / self.version
            rmtree(session_path, ignore_errors=True)
            copytree(self.path, session_path, ignore=ignore_patterns(*gridignore.generate(src=self.path)))

            yield session_path

        finally:
            rmtree(session_path, ignore_errors=True)

    def _prune_cache(self) -> None:
        """Prunes cache; only keeps the 10 most recent items. """
        packages = sorted(self.cache_location.iterdir(), key=os.path.getmtime)
        for package in packages[10:]:
            if package.is_file():
                package.unlink(missing_ok=True)

    def package(self) -> Path:
        """Packages local path using tar."""
        if self.package_path.exists():
            return self.package_path

        # create a packaging session if not available
        with self.packaging_session() as session_path:
            tar_path(source_path=session_path, target_file=self.package_path, compression=True)

        return self.package_path

    def upload(self, url: str) -> None:
        """Uploads package to URL, usually pre-signed URL."""
        uploader = S3Uploader(
            presigned_urls={1: url},
            already_uploaded_parts=[],
            source_file=str(self.package_path),
            name=self.package_path.name,
            total_size=self.package_path.stat().st_size,
            split_size=self.package_path.stat().st_size
        )

        uploader.upload()
