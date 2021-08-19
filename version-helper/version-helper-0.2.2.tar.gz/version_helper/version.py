import pathlib
import re

from version_helper import Git

SEMVER_PATTERN = r'^(?P<major>0|(?:[1-9]\d*))(?:\.(?P<minor>0|(?:[1-9]\d*))(?:\.(?P<patch>0|(?:[1-9]\d*)))(?:\-(?P<prerelease>[\w\d\.-]+))?(?:\+(?P<build>[\w\d\.-]+))?)?$'

GIT_DESCRIBE_CORE_PATTERN = r'^(?P<core>(?P<major>0|(?:[1-9]\d*))(?:\.(?P<minor>0|(?:[1-9]\d*)))(?:\.(?P<patch>0|(?:[1-9]\d*))))'
GIT_DESCRIBE_BUILD_PATTERN = r'\-(?P<build>(?:\d+\-g[\w\d]{7,})?(?:\-)?(?:dirty)?)$'


class Version:
    """Semantic Versioning compatible class for parsing and emitting SemVer strings into a `Version` object

    More details on Semantic Versioning can be found at https://semver.org/
    """

    def __init__(self, major: int, minor: int, patch: int,
                 prerelease: str = None, build: str = None):
        """Create a `Version` object with the given attributes

        :param major: MAJOR version when you make incompatible API changes
        :param minor: MINOR version when you add functionality in a backwards compatible manner
        :param patch: PATCH version when you make backwards compatible bug fixes
        :param prerelease: Pre-release version string like `alpha.0` or `beta.3`
        :param build: Build metadata
        """
        self.major: int = major
        self.minor: int = minor
        self.patch: int = patch
        self.prerelease: str = prerelease
        self.build: str = build

    def __repr__(self):
        return self.full

    def __str__(self):
        return self.full

    @staticmethod
    def parse(string: str, is_from_git_describe: bool = False) -> 'Version':
        """Parse a version string into it's individual Semantic Versioning parts

        :param string: A Semantic Versioning string
        :param is_from_git_describe: Whether or not the version string is from `git describe`
        :return: A `Version` class object
        """
        version_dict = {}

        # parse SemVer string
        if string and not is_from_git_describe:
            semver = re.fullmatch(SEMVER_PATTERN, string.strip())
            if semver:
                version_dict = semver.groupdict()

        # parse git describe string
        if string and is_from_git_describe:
            version_string = string.strip()
            core = re.search(GIT_DESCRIBE_CORE_PATTERN, version_string)
            build = re.search(GIT_DESCRIBE_BUILD_PATTERN, version_string)

            if core:
                version_dict.update(core.groupdict())
                version_string = version_string.replace(f'{version_dict.get("core")}', '').strip('-')

                if build:
                    version_dict.update(build.groupdict())
                    version_string = version_string.replace(f'{version_dict.get("build")}', '').strip('-')

                if version_string:
                    version_dict.setdefault('prerelease', version_string)

        if not all(k in version_dict for k in ['major', 'minor', 'patch']):
            raise ValueError(f'"{string}" is not valid to Semantic Versioning Specification')

        return Version(
            major=int(version_dict.get('major')),
            minor=int(version_dict.get('minor')),
            patch=int(version_dict.get('patch')),
            prerelease=version_dict.get('prerelease'),
            build=version_dict.get('build'),
        )

    @classmethod
    def get_from_git_describe(cls, dirty=False) -> 'Version':
        """Get a semantic version from git describe

        :param dirty: Append '-dirty' to the build context, if the working tree has local modifications
        :return: A `Version` class object
        """
        description = Git.describe(dirty=dirty)
        return cls.parse(description, True)

    def set(self, major: int, minor: int, patch: int,
            prerelease: str = None, build: str = None):
        """Set `Version` attributes

        :param major: MAJOR version when you make incompatible API changes
        :param minor: MINOR version when you add functionality in a backwards compatible manner
        :param patch: PATCH version when you make backwards compatible bug fixes
        :param prerelease: Pre-release version string like `alpha.0` or `beta.3`
        :param build: Build metadata
        """
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    @property
    def core(self) -> str:
        """Core version string including major, minor and patch

        :return: Core version string
        """
        return f'{self.major}.{self.minor}.{self.patch}'

    @property
    def full(self) -> str:
        """Full Semantic Version string including prerelease and build metadata

        :return: Full version string with all it's Semantic Versioning parts
        """
        semver = f'{self.major}.{self.minor}.{self.patch}'
        if self.prerelease:
            semver += f'-{self.prerelease}'
        if self.build:
            semver += f'+{self.build}'
        return semver

    @staticmethod
    def read_from_file(file: pathlib.Path, variable_name: str = '__version__', separator: str = '=') -> 'Version':
        """Reading a version string from a file.

        The version string in the `file` could be stored as simple text
        or as a value assigned to a `variable_name` with a `separator`.
        Other variables, above or below the version assignment (`variable_name`),
        are allowed in the `file` to read from.

        :param file: Path-like object to the file containing the version string
        :param variable_name: Name of the variable, where the version string is assigned to
        :param separator: Separator between the variables name and the assigned version string.
        :return: A `Version` object with the parsed version string from the `file`
        """
        if not separator and variable_name:
            raise ValueError('None value for separator. Could not parse file.')
        if not variable_name and separator:
            raise ValueError('None value for variable_name. Could not parse file.')

        version_string = None

        if file.suffix == '.py':
            if separator != '=':
                raise ValueError('Only "=" is allowed as separator for .py files. Could not parse file.')

            # load python file as module
            from importlib.util import spec_from_loader, module_from_spec
            from importlib.machinery import SourceFileLoader

            spec = spec_from_loader("version_file", SourceFileLoader("version_file", str(file.absolute())))
            version_file = module_from_spec(spec)
            spec.loader.exec_module(version_file)

            # get version string
            version_string = eval(f"version_file.{variable_name}")
        else:
            with open(file, 'r') as f:
                line = f.readline().strip()
                while line:
                    if variable_name and separator:
                        if line.startswith(variable_name):
                            version_string = line.split(separator, 1)[1].strip()
                            break
                    else:
                        version_string = line.strip()
                        break
                    line = f.readline().strip()

            # clean version string and remove single and double quotes
            version_string = version_string.replace('"', '')
            version_string = version_string.replace("'", "")

        return Version.parse(version_string)

    def write_to_file(
            self,
            file: pathlib.Path,
            variable_name: str = '__version__',
            separator: str = '=',
            version_type: str = 'full',
            quote_version: bool = True,
            encoding: str = 'utf-8',
    ) -> int:
        """Writing a version string to a file

        :param file: Path-like object to the file containing the version string
        :param variable_name: Name of the variable, where the version string is assigned to
        :param separator: Separator between the variables name and the assigned version string.
        :param version_type: Type of the version to write to the file. ['core', 'full']
        :param quote_version: Adds double-quotes around the version string
        :param encoding: Encoding of the file to write
        :return: The number of bytes written
        """
        data = ''
        if variable_name and separator:
            data += f'{variable_name}{separator}'

        version_string = ''
        if version_type == 'core':
            version_string = self.core
        elif version_type == 'full':
            version_string = self.full

        if quote_version:
            data += f'"{version_string}"'
        else:
            data += version_string

        return file.write_text(data, encoding=encoding)
