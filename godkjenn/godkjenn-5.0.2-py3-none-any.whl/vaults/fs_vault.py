"""Simple file-system based implementation of a vault.
"""

from enum import Enum
import json
from pathlib import Path
import shutil

from godkjenn.artifact import Artifact


class FSVault:
    """File-system implementation of a vault.

    This just keeps accepted data in files with the "accepted" suffix and received data in files suffixed with
    "received". Id's in this vault are simply paths.

    This assumes it has complete control over the files under `root_directory`.

    Args:
        root_path: The root directory under which this will store received and accepted data.
    """

    def __init__(self, root_path):
        self._root_path = Path(root_path)

    @property
    def root_path(self) -> Path:
        "Root path of the vault."
        return self._root_path

    def accepted(self, test_id) -> Artifact:
        """Get the current accepted value for `test_id`.

        Args:
            test_id: ID of the test.

        Returns: An Artifact instance.

        Raises:
            KeyError: `test_id` does not have accepted data in the vault.
        """
        return self._get(test_id, _Kind.accepted)

    def accept(self, test_id):
        """Accept the current received data for `test_id`.

        Args:
            test_id: The ID of the test to accept.

        Raises:
            KeyError: There is no received data for `test_id`.
        """
        received_dir = self._artifact_dir_path(test_id, _Kind.received)
        if not received_dir.exists():
            raise KeyError(f"No received data for {test_id}")

        accepted_dir = self._artifact_dir_path(test_id, _Kind.accepted)
        if accepted_dir.exists():
            shutil.rmtree(accepted_dir)

        shutil.move(received_dir, accepted_dir)

    def received(self, test_id) -> Artifact:
        """Get the current received value for `test_id`.

        Args:
            test_id: ID of test.

        Returns: An Artifact describing the received data `test_id`.

        Raises:
            KeyError: There is no received data for `test_id`.
        """
        return self._get(test_id, _Kind.received)

    def receive(self, test_id, data, mime_type, encoding):
        """Set new received data for a test.

        Args:
            test_id: ID of the test for which to receive data.
            artifact: Artifact describing received data for the test.
        """
        self._put(test_id, _Kind.received, data, mime_type, encoding)

    def ids(self):
        """Get all IDs in the vault.

        This is all IDs that have either or both of accepted and received data. There is no
        order to the results. Each ID is included only once in the output, even if it has both
        received and accepted data.

        Returns: An iterable of all test IDs.
        """
        return set(
            str(path.parent.relative_to(self._root_path))
            for kind in _Kind
            for path in self._root_path.glob("**/{}".format(kind.value))
        )

    def _artifact_dir_path(self, test_id, kind):
        return self._root_path / test_id / kind.value

    def _artifact_file_paths(self, test_id, kind):
        return (
            self._artifact_dir_path(test_id, kind) / "data",
            self._artifact_dir_path(test_id, kind) / "metadata.json",
        )

    def _get(self, test_id, kind):
        data_path, metadata_path = self._artifact_file_paths(test_id, kind)

        if not data_path.exists():
            raise KeyError("no {} data: {}".format(kind.value, test_id))

        if not metadata_path.exists():
            raise KeyError("no {} metadata: {}".format(kind.value, test_id))

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        try:
            mime_type = metadata["mime-type"]
        except KeyError as err:
            raise KeyError("No mime-type in metadata") from err

        encoding = metadata.get("encoding", None)

        return Artifact(data_path, mime_type=mime_type, encoding=encoding)

    def _put(self, test_id, kind, data, mime_type, encoding):
        data_path, metadata_path = self._artifact_file_paths(test_id, kind)
        data_path.parent.mkdir(parents=True, exist_ok=True)

        data_path.write_bytes(data)

        metadata = {"mime-type": mime_type, "encoding": encoding}
        with metadata_path.open("wt", encoding="utf-8") as handle:
            json.dump(metadata, handle)


class _Kind(Enum):
    accepted = "accepted"
    received = "received"
