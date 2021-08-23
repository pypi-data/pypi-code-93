import os
import subprocess
from textwrap import dedent

import requests
from mock import Mock, patch
from pyrpkg import Modulemd

from utils import CommandTestCase

try:
    import unittest2 as unittest
except ImportError:
    import unittest


EOG_MODULEMD = """
document: modulemd
version: 2
data:
  name: eog
  stream: f28
  version: 20170629213428
  summary: Eye of GNOME Application Module
  description: The Eye of GNOME image viewer (eog) is the official image viewer for
    the GNOME desktop. It can view single image files in a variety of formats, as
    well as large image collections.
  license:
    module: [MIT]
  dependencies:
  - buildrequires:
      flatpak-runtime: [f28]
    requires:
      flatpak-runtime: [f28]
  profiles:
    default:
      rpms: [eog]
  components:
    rpms: {}
  xmd:
    mbs: OMITTED
"""

FLATPAK_RUNTIME_MODULEMD = """
document: modulemd
version: 2
data:
  name: flatpak-runtime
  stream: f28
  version: 20170701152209
  summary: Flatpak Runtime
  description: Libraries and data files shared between applications
  api:
    rpms: [librsvg2, gnome-themes-standard, abattis-cantarell-fonts, rest, xkeyboard-config,
      adwaita-cursor-theme, python3-gobject-base, json-glib, zenity, gsettings-desktop-schemas,
      glib-networking, gobject-introspection, gobject-introspection-devel, flatpak-rpm-macros,
      python3-gobject, gvfs-client, colord-libs, flatpak-runtime-config, hunspell-en-GB,
      libsoup, glib2-devel, hunspell-en-US, at-spi2-core, gtk3, libXtst, adwaita-gtk2-theme,
      libnotify, adwaita-icon-theme, libgcab1, libxkbcommon, libappstream-glib, python3-cairo,
      gnome-desktop3, libepoxy, hunspell, libgusb, glib2, enchant, at-spi2-atk]
  dependencies:
  - buildrequires:
      platform: [f28]
    requires:
      platform: [f28]
  license:
    module: [MIT]
  profiles:
    buildroot:
      rpms: [flatpak-rpm-macros, flatpak-runtime-config]
    runtime:
      rpms: [libwayland-server, librsvg2, libX11, libfdisk, adwaita-cursor-theme,
        libsmartcols, popt, gdbm, libglvnd, openssl-libs, gobject-introspection, systemd,
        ncurses-base, lcms2, libpcap, crypto-policies, fontconfig, libacl, libwayland-cursor,
        libseccomp, gmp, jbigkit-libs, bzip2-libs, libunistring, freetype, nettle,
        libidn, python3-six, gtk2, gtk3, ca-certificates, libdrm, rest, lzo, libcap,
        gnutls, pango, util-linux, basesystem, p11-kit, libgcab1, iptables-libs, dbus,
        python3-gobject-base, cryptsetup-libs, krb5-libs, sqlite-libs, kmod-libs,
        libmodman, libarchive, enchant, libXfixes, systemd-libs, shared-mime-info,
        coreutils-common, libglvnd-glx, abattis-cantarell-fonts, cairo, audit-libs,
        libwayland-client, libpciaccess, sed, libgcc, libXrender, json-glib, libxshmfence,
        glib-networking, libdb, fedora-modular-repos, keyutils-libs, hwdata, glibc,
        libproxy, python3-pyparsing, device-mapper, libgpg-error, system-python, shadow-utils,
        libXtst, libstemmer, dbus-libs, libpng, cairo-gobject, libXau, pcre, python3-packaging,
        at-spi2-core, gawk, mesa-libglapi, libXinerama, adwaita-gtk2-theme, libX11-common,
        device-mapper-libs, python3-appdirs, libXrandr, bash, glibc-common, libselinux,
        elfutils-libs, libxkbcommon, libjpeg-turbo, libuuid, atk, acl, libmount, lz4-libs,
        ncurses, libgusb, glib2, python3, libpwquality, at-spi2-atk, libattr, libcrypt,
        gnome-themes-standard, libtiff, harfbuzz, libstdc++, libXcomposite, xkeyboard-config,
        libxcb, libnotify, systemd-pam, readline, libXxf86vm, python3-cairo, gtk-update-icon-cache,
        python3-pip, mesa-libEGL, zenity, python3-gobject, libXcursor, tzdata, gvfs-client,
        libverto, libblkid, cracklib, libusbx, libcroco, libdatrie, gdk-pixbuf2, libXi,
        qrencode-libs, python3-libs, graphite2, mesa-libwayland-egl, mesa-libGL, pixman,
        libXext, glibc-all-langpacks, info, grep, fedora-modular-release, setup, zlib,
        libtasn1, libepoxy, hunspell, libsemanage, python3-setuptools, fontpackages-filesystem,
        libsigsegv, hicolor-icon-theme, libxml2, expat, libgcrypt, emacs-filesystem,
        gsettings-desktop-schemas, chkconfig, xz-libs, mesa-libgbm, libthai, coreutils,
        colord-libs, libcap-ng, flatpak-runtime-config, elfutils-libelf, hunspell-en-GB,
        libsoup, pam, hunspell-en-US, jasper-libs, p11-kit-trust, avahi-libs, elfutils-default-yama-scope,
        libutempter, adwaita-icon-theme, ncurses-libs, libidn2, system-python-libs,
        libffi, libXdamage, libglvnd-egl, libXft, cups-libs, ustr, libcom_err, libappstream-glib,
        gnome-desktop3, gdk-pixbuf2-modules, libsepol, filesystem, gzip, mpfr]
    sdk:
      rpms: [gcc]
  components:
    rpms: {}
  xmd:
    flatpak:
      # This gives information about how to map this module into Flatpak terms
      # this is used when building application modules against this module.
      branch: f28
      runtimes: # Keys are profile names
        runtime:
          id: org.fedoraproject.Platform
          sdk: org.fedoraproject.Sdk
        sdk:
          id: org.fedoraproject.Sdk
          runtime: org.fedoraproject.Platform
    mbs: OMITTED
"""  # noqa

UNEXPANDED_MODULEMD = """
document: modulemd
version: 2
data:
  name: nodeps
  stream: f28
  version: 20181234567890
  summary: No dependencies
  description: This module has no deps
  license:
    module: [MIT]
  dependencies:
  - buildrequires:
      platform: [f27, f28]
    requires:
      platform: [f27, f28]
  components:
    rpms: {}
"""

NODEPS_MODULEMD = """
document: modulemd
version: 2
data:
  name: nodeps
  stream: f28
  version: 20181234567890
  summary: No dependencies
  description: This module has no deps
  license:
    module: [MIT]
  dependencies: []
  components:
    rpms: {}
"""

BUILDS = {
    'eog:f28': [
        {'modulemd': EOG_MODULEMD}
    ],
    'eog:f28:20170629213428': [
        {'modulemd': EOG_MODULEMD}
    ],
    'flatpak-runtime:f28': [
        {'modulemd': FLATPAK_RUNTIME_MODULEMD}
    ],
    'bad-modulemd:f28': [
        {'modulemd': "BLAH"}
    ],
    'unexpanded:f28': [
        {'modulemd': UNEXPANDED_MODULEMD}
    ],
    'nodeps:f28': [
        {'modulemd': NODEPS_MODULEMD}
    ],
}


@unittest.skipIf(
    Modulemd is None,
    'Skip on old Python versions where libmodulemd is not available.')
class FlatpakBuildCase(CommandTestCase):
    def set_container_modules(self, container_modules):
        with open(os.path.join(self.repo_path, 'container.yaml'), 'w') as f:
            f.write(dedent("""\
                compose:
                    modules: {0}
                """.format(container_modules)))
        git_cmds = [
            ['git', 'add', 'container.yaml'],
            ['git', 'commit', '-m', 'Update container.yaml'],
        ]
        for cmd in git_cmds:
            self.run_cmd(cmd, cwd=self.repo_path,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_cmds = [
            ['git', 'fetch', 'origin'],
            ['git', 'reset', '--hard', 'origin/master'],
        ]
        for cmd in git_cmds:
            self.run_cmd(cmd, cwd=self.cloned_repo_path,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def setUp(self):
        super(FlatpakBuildCase, self).setUp()

        self.cmd = self.make_commands()
        self.cmd.module_api_url = "https://mbs.example.com/module-build-service/1/"

        self.requests_get_p = patch('requests.get')
        self.mock_requests_get = self.requests_get_p.start()

        def mock_get(url, params=None, timeout=None):
            nsvc = params['nsvc']
            del params['nsvc']
            self.assertEqual(params, {
                'order_desc_by': 'version',
                'per_page': 1
            })

            response = Mock(requests.Response)
            response.ok = True
            response.json.return_value = {'items': BUILDS.get(nsvc, [])}

            return response

        self.mock_requests_get.side_effect = mock_get

        self.load_krb_user_p = patch('pyrpkg.Commands._load_krb_user')
        self.mock_load_krb_user = self.load_krb_user_p.start()

        session = Mock()
        self.kojisession = session
        session.system.listMethods.return_value = ['buildContainer']

        def load_kojisession(self):
            self._kojisession = session

        self.load_kojisession_p = patch('pyrpkg.Commands.load_kojisession',
                                        new=load_kojisession)
        self.mock_load_kojisession = self.load_kojisession_p.start()

        session.getBuildTarget.return_value = {'dest_tag': 'f28-flatpak'}
        session.getTag.return_value = {'locked': False}

    def tearDown(self):
        self.requests_get_p.stop()
        self.load_krb_user_p.stop()
        self.load_kojisession_p.stop()

        super(FlatpakBuildCase, self).tearDown()

    def test_find_target(self):
        self.set_container_modules(['eog:f28'])
        assert self.cmd.flatpak_build_target == 'f28-flatpak-candidate'

    def test_find_target_version(self):
        self.set_container_modules(['eog:f28:20170629213428'])
        assert self.cmd.flatpak_build_target == 'f28-flatpak-candidate'

    def test_find_target_profile(self):
        self.set_container_modules(['eog:f28/sdk'])
        assert self.cmd.flatpak_build_target == 'f28-flatpak-candidate'

    def module_failure(self, container_modules, exception_str):
        if container_modules is not None:
            self.set_container_modules(container_modules)
        with self.assertRaises(Exception) as e:
            self.cmd.load_flatpak_build_target()
        self.assertIn(exception_str, str(e.exception))

    def test_find_target_no_container_yaml(self):
        self.module_failure(None, "Cannot find 'container.yaml'")

    def test_find_target_no_modules(self):
        self.module_failure([], "No modules listed in 'container.yaml'")

    def test_find_target_multiple_modules(self):
        self.module_failure(['eog:f28', 'foo:f28'],
                            "Multiple modules listed in 'container.yaml'")

    def test_find_target_bad_nsv(self):
        self.module_failure(['NOT_A_MODULE'], "should be NAME:STREAM[:VERSION]")

    def test_find_target_no_builds(self):
        self.module_failure(['eog:f1'], "Cannot find any builds for module")

    def test_find_target_bad_modulemd(self):
        self.module_failure(['bad-modulemd:f28'], "Failed to load modulemd")

    def test_find_target_unexpected(self):
        self.module_failure(['unexpanded:f28'], "stream list for 'platform' is not expanded")

    def test_find_target_no_platform(self):
        self.module_failure(['nodeps:f28'], "Unable to find 'platform' module in the dependencies")

    def test_flatpak_build(self):
        self.set_container_modules(['eog:f28'])
        self.cmd.container_build_koji(nowait=True, flatpak=True)

        session = self.kojisession
        session.getBuildTarget.assert_called_with('f28-flatpak-candidate')
        session.getTag.assert_called_with('f28-flatpak')

        session.buildContainer.assert_called()
        args, kwargs = session.buildContainer.call_args
        source, container_target, taskinfo = args

        assert container_target == 'f28-flatpak-candidate'
