import os
import shutil

from ievv_opensource.utils.ievvbuildstatic import filepath
from ievv_opensource.utils.ievvbuildstatic import pluginbase


class Plugin(pluginbase.Plugin):
    """
    Media copy plugin --- copies media files from staticsources into
    the static directory, and supports watching for file changes.

    Examples:

        Copy a file ``demoapp/staticsources/demoapp/media/cool.txt`` into
        ``demoapp/static/1.0.0/media/cool.txt``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.mediacopy.Plugin(sourcefile="cool.txt"),
                    ]
                )
            )

        Using a different source folder. This will copy
        all files in ``demoapp/staticsources/demoapp/assets/`` into
        ``demoapp/static/1.0.0/assets/``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.mediacopy.Plugin(sourcefile="image.jpg"),
                    ]
                )
            )
    """
    name = 'singlemediacopy'

    def __init__(self, sourcefile, destinationfile=None, **kwargs):
        """
        Parameters:
            sourcefile: The folder where media files is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                You can specify a folder in another app using
                a :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath` object.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.sourcefile = sourcefile
        if isinstance(sourcefile, filepath.FilePathInterface) and destinationfile is None:
            raise ValueError('destinationfile must be specifed when sourcefile is not a string.')
        self.destinationfile = destinationfile or sourcefile

    def get_sourcefile_path(self):
        return self.app.get_source_path(self.sourcefile)

    def get_destinationfile_path(self):
        return self.app.get_destination_path(self.destinationfile)

    def run(self):
        sourcefile = self.get_sourcefile_path()
        self.get_logger().command_start('Copying single media media')
        if not os.path.exists(sourcefile):
            self.get_logger().warning('Media source file, {}, does not exist.'.format(
                sourcefile))
            return

        destinationfile = self.get_destinationfile_path()
        if os.path.abspath(destinationfile) == os.path.abspath(sourcefile):
            raise ValueError('mediacopy: sourcefile {} is the same as destinationfile {}'.format(
                sourcefile, destinationfile))

        if os.path.exists(destinationfile):
            self.get_logger().debug('Removing {}'.format(destinationfile))
            os.remove(destinationfile)

        self.get_logger().debug('Copying {} -> {}'.format(sourcefile, destinationfile))
        shutil.copyfile(sourcefile, destinationfile)
        self.get_logger().command_success('Copied media successfully :)')

    def get_watch_folders(self):
        """
        We only watch the folder where the less sources are located,
        so this returns the absolute path of the ``sourcefile``.
        """
        return []

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefile)
