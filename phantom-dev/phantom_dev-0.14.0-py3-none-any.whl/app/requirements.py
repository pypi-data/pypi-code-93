from logging import getLogger
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


logger = getLogger(name=__name__)



def download_wheels(requirements_file: Path, destination: Path):
	with TemporaryDirectory() as tmp:
		pip_args = [
			sys.executable,
			'-m',
			'pip',
			'download',
			'--platform', 'manylinux1_x86_64',
			'--python-version', '3.6',
			'--implementation', 'cp',
			'--abi', 'cp36m',
			'--prefer-binary',
			'--only-binary', ':all:',
			'--requirement', str(requirements_file),
			'--dest', tmp,
		]
		logger.debug('Running pip.main with args %r', pip_args)
		subprocess.run(
			args=pip_args, check=True, stdout=sys.stdout, stderr=sys.stderr)
		for tmp_wheel in Path(tmp).iterdir():
			wheel_path = destination.joinpath(tmp_wheel.name)
			tmp_wheel.rename(wheel_path)
			yield wheel_package_name(wheel_path), wheel_path


def download_sdists(requirements_file: Path, destination: Path):
	with TemporaryDirectory() as tmp:
		pip_args = [
			sys.executable,
			'-m',
			'pip',
			'download',
			'--python-version', '3.6',
			'--no-binary', ':all:',
			'--no-deps',
			'--requirement', str(requirements_file),
			'--dest', tmp,
		]
		logger.debug('Running pip.main with args %r', pip_args)
		subprocess.run(
			args=pip_args, check=True, stdout=sys.stdout, stderr=sys.stderr)
		for tmp_sdist in Path(tmp).iterdir():
			sdist_path = destination.joinpath(tmp_sdist.name)
			tmp_sdist.rename(sdist_path)
			yield sdist_package_name(sdist_path), sdist_path



def download_requirements(
	destination: Path,
	wheel_requirements_file,
	sdist_requirements_file,
):
	if sdist_requirements_file.exists():
		yield from download_sdists(sdist_requirements_file, destination)

	if wheel_requirements_file.exists():
		yield from download_wheels(wheel_requirements_file, destination)


def wheel_package_name(wheel: Path):
	logger.debug('Getting package name from %r', wheel)
	with ZipFile(wheel) as wheel_zip:
		metadata_items = []
		for item_info in wheel_zip.infolist():
			item_path = Path(item_info.filename)
			try:
				parent_name, name = item_path.parts
			except ValueError:
				continue

			if name != 'METADATA':
				continue

			if not parent_name.endswith('.dist-info'):
				continue

			metadata_items.append(item_info.filename)

		try:
			metadata_path, = metadata_items
		except ValueError:
			raise ValueError(
				'Unable to resolve metadata file from candidates'
				f' {metadata_items}'
			)

		with wheel_zip.open(metadata_path) as metadata:
			return metadata_name(metadata_file=metadata)


def sdist_package_name(sdist: Path):
	with tarfile.open(sdist, mode='r:gz') as sdist_tar:
		metadata_items = []
		for item_info in sdist_tar.getmembers():
			item_path = Path(item_info.name)
			try:
				_, name = item_path.parts
			except ValueError:
				continue

			if name == 'PKG-INFO':
				metadata_member = item_info
				break

		else:
			raise ValueError(
				'Unable to resolve metadata file from candidates'
				f' {metadata_items}'
			)

		metadata = sdist_tar.extractfile(metadata_member)
		return metadata_name(metadata_file=metadata)


def metadata_name(metadata_file):
	for line in metadata_file.readlines():
		if line.startswith(b'Name: '):
			_, package_name = line.strip().split(b': ')
			return package_name.decode()

	raise KeyError("No 'Name' entry in wheel metadata")


if __name__ == '__main__':
	import sys
	print(wheel_package_name(sys.argv[1]))
