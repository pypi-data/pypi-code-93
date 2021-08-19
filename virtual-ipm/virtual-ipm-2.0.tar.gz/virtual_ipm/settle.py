#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import platform
import os
import subprocess
import sys
import tempfile

_not_installed_error = ImportError("Virtual-IPM doesn't seem to be installed")

try:
    import virtual_ipm
except ImportError:
    raise _not_installed_error


def compute_vipm_icon_path():
    base_path = os.path.join(
        os.path.split(virtual_ipm.__file__)[0],
        'frontends',
        'gui',
        'icons'
    )
    if platform.system().lower() == 'linux':
        return os.path.join(base_path, 'vipm.png')
    elif platform.system().lower() == 'windows':
        return os.path.join(base_path, 'vipm-windows.ico')
    else:
        raise EnvironmentError('Unsupported platform: %s' % platform.system())


def version():
    version_file = os.path.join(
        os.path.split(virtual_ipm.__file__)[0],
        'VERSION'
    )
    with open(version_file) as f:
        return f.read()


def on_linux():
    start_actions = []
    virtualenv = os.getenv('VIRTUAL_ENV')
    if virtualenv:
        start_actions.append(
            '/usr/bin/env PATH={0}:$PATH'.format(
                os.path.join(virtualenv, 'bin')
            )
        )
    try:
        path_to_exec = subprocess.check_output(['which', 'virtual-ipm-gui']).strip()
    except subprocess.CalledProcessError:
        raise _not_installed_error
    if isinstance(path_to_exec, bytes):
        path_to_exec = path_to_exec.decode('utf-8')
    start_actions.append(path_to_exec)
    desktop_entry_path = os.path.expanduser('~/.local/share/applications/virtual-ipm.desktop')
    desktop_entry = (
        '[Desktop Entry]\n'
        'Version=%(Version)s\n'
        'Name=Virtual-IPM GUI\n'
        'Exec=%(Exec)s\n'
        'Terminal=false\n'
        'Type=Application\n'
        'Icon=%(Icon)s'
    )
    desktop_entry %= {
        'Version': version(),
        'Exec': ' '.join(start_actions),
        'Icon': compute_vipm_icon_path(),
    }

    if os.path.exists(desktop_entry_path):
        overwrite = input('Desktop entry already exists; overwrite? [y/n] ')
        if overwrite != 'y':
            return

    try:
        with open(str(desktop_entry_path), str('w')) as fp:
            fp.write(str(desktop_entry))
    except IOError as err:
        print(
            'Could not create desktop entry at {0}: {1}'.format(
                desktop_entry_path,
                str(err)
            )
        )
    else:
        print('Created desktop entry at {0}'.format(desktop_entry_path))

    return 0


def on_windows():
    vb_script_template = (
        'Set oWS = WScript.CreateObject("WScript.Shell")\n'
        'sLinkFile = "%(symlink-path)s"\n'
        'Set oLink = oWS.CreateShortcut(sLinkFile)\n'
        'oLink.TargetPath = "%(batch-path)s"\n'
        'oLink.Description = "Virtual-IPM GUI"\n'
        'oLink.IconLocation = "%(icon-path)s"\n'
        'oLink.Save'
    )

    app_data_dir = os.path.split(os.getenv('appdata'))[0]
    app_data_vipm_dir = os.path.join(
        app_data_dir,
        'Local',
        'Virtual-IPM'
    )
    batch_path = os.path.join(
        app_data_vipm_dir,
        'start-virtual-ipm-gui.bat'
    )

    symlink_path = os.path.join(
        os.path.expanduser('~'),
        'Desktop',
        'Virtual-IPM-GUI.lnk'
    )

    vb_script_content = vb_script_template % {
        'symlink-path': symlink_path,
        'batch-path': batch_path,
        'icon-path': compute_vipm_icon_path(),
    }

    batch_template = (
        'set PATH={0}\n'
        'virtual-ipm-gui'
    )
    batch_content = batch_template.format(os.getenv('PATH'))

    if not os.path.exists(app_data_vipm_dir):
        os.mkdir(app_data_vipm_dir)
    with open(batch_path, str('w')) as fp:
        fp.write(str(batch_content))

    vbs_file = tempfile.NamedTemporaryFile(suffix='.vbs')
    vbs_file_name = vbs_file.name
    vbs_file.close()

    with open(vbs_file_name, str('w')) as fp:
        fp.write(str(vb_script_content))

    subprocess.call(['cscript', vbs_file.name])

    return 0


def main():
    if platform.system().lower() == 'linux':
        return on_linux()
    elif platform.system().lower() == 'windows':
        return on_windows()
    else:
        print('Settling on {0} is not supported'.format(platform.system()))
        return -1

if __name__ == '__main__':
    sys.exit(main())
