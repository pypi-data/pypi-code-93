"""Manage the understory from your desktop."""

# import argparse
import configparser
import json
import os
import pathlib
import random
import textwrap
import time
import webbrowser

try:
    import sh
except ImportError:
    pass

from . import digitalocean, dynadot

__all__ = ["digitalocean", "dynadot", "Gaea", "main"]

LOGO = """\
 ██████╗  █████╗ ███████╗ █████╗ 
██╔════╝ ██╔══██╗██╔════╝██╔══██╗
██║  ███╗███████║█████╗  ███████║
██║   ██║██╔══██║██╔══╝  ██╔══██║
╚██████╔╝██║  ██║███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""

STARTED = False
DHPARAM_BITS = 512  # FIXME 4096 for production (perform in bg post install)
SSL_CIPHERS = ":".join(
    (
        "ECDHE-RSA-AES256-GCM-SHA512",
        "DHE-RSA-AES256-GCM-SHA512",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "DHE-RSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-SHA384",
    )
)
APTITUDE_PACKAGES = (
    "build-essential",  # build tools
    "expect",  # ssh password automation
    "psmisc",  # killall
    "xz-utils",  # .xz support
    "libbz2-dev",  # bz2 support
    "zip",  # .zip support
    "git",
    "fcgiwrap",  # Git w/ HTTP serving
    "supervisor",  # service manager
    "redis-server",  # Redis key-value database
    "haveged",  # produces entropy for faster key generation
    # XXX "sqlite3",  # SQLite flat-file relational database
    "libicu-dev",
    "python3-icu",  # SQLite unicode collation
    "libsqlite3-dev",  # SQLite Python extension loading
    "libssl-dev",  # uWSGI SSL support
    "cargo",  # rust (pycryptography)
    "libffi-dev",  # rust (pycryptography)
    "zlib1g-dev",
    "python3-dev",  # Python build dependencies
    "python3-crypto",  # pycrypto
    "python3-libtorrent",  # libtorrent
    "ffmpeg",  # a/v en/de[code]
    "imagemagick",  # heic -> jpeg
    "libsm-dev",
    "python-opencv",  # opencv
    "libevent-dev",  # Tor
    "pandoc",  # markup translation
    "graphviz",  # graphing
    "libgtk-3-0",
    "libdbus-glib-1-2",  # Firefox
    "xvfb",
    "x11-utils",  # browser automation
    "libenchant-dev",  # pyenchant => sopel => bridging IRC
    "ufw",  # an Uncomplicated FireWall
    "tmux",  # automatable terminal multiplexer
)
VERSIONS = {
    "python": "3.9.2",
    "nginx": "1.18.0",
    "tor": "0.4.4.5",
    "firefox": "82.0",
    "geckodriver": "0.27.0",
}


def build_linux():
    """
    Compile a standalone binary for distribution on linux systems.

    Upload binary to the bootstrap server upon successful compilation.

    Call from inside the project's working directory using `poetry run build_linux`

    """
    if sh.poetry(
        "run",
        "python",
        "-m",
        "nuitka",
        "main.py",
        "--plugin-enable=pyside6",
        "--plugin-enable=gevent",
        "--onefile",
        "-o",
        "dist/gaea",
        "--output-dir=dist",
        "--linux-onefile-icon=icon.png",
    ).exit_code:
        print("build failed!")
    else:
        sh.scp(
            "-i", "gaea_key", "./dist/gaea", "root@137.184.4.213:/var/www/html/dists/"
        )
        print("build uploaded!")


def build_windows():
    pass


def build_macos():
    pass


def spawn_cloud(name, digitalocean_token):
    """Spawn the understory on a new droplet."""
    cli = digitalocean.Client(digitalocean_token)
    key = digitalocean.get_key(cli)
    print("generating droplet:", end=" ", flush=True)
    droplet = cli.create_droplet(name, size="1gb", ssh_keys=[key["id"]])
    digitalocean.wait(cli, droplet["id"])
    droplet = cli.get_droplet(droplet["id"])
    ip_address = None
    for ip_details in droplet["networks"]["v4"]:
        if ip_details["type"] == "public":
            ip_address = ip_details["ip_address"]
            break
    print(ip_address, flush=True)

    print("spawning gaea..", flush=True)
    root_ssh = digitalocean.get_ssh("root", ip_address)
    root_ssh("adduser gaea --disabled-login --gecos gaea")
    root_ssh('echo "gaea  ALL=NOPASSWD: ALL" | tee -a /etc/sudoers.d/01_gaea')

    gaea_ssh_dir = "/home/gaea/.ssh"
    root_ssh(f"mkdir {gaea_ssh_dir}")
    root_ssh(f"cp /root/.ssh/authorized_keys {gaea_ssh_dir}")
    root_ssh(f"chown gaea:gaea {gaea_ssh_dir} -R")

    root_ssh("apt install fuse -y")

    print("spawning the understory..", flush=True)
    print("__file__:", __file__)
    digitalocean.scp("gaea", f"gaea@{ip_address}:")
    gaea_ssh = digitalocean.get_ssh("gaea", ip_address)
    gaea_ssh("chown gaea:gaea gaea")
    gaea_ssh("chmod u+x gaea")
    gaea_ssh(f"./gaea setup {digitalocean_token}", process_out(ip_address))


# def spawn_local():
#     # sh.sudo("bash", "spawn.sh")  # TODO FIXME
#
#     # sh.scp("-i", "gaea_key", "gaea", "gaea@localhost:")
#
#     # TODO sh bake
#     def ssh(command):
#         sh.ssh(
#             "gaea@localhost", "-i", "gaea_key", command,
#             _out=process_out("localhost")
#         )
#
#     # ssh("chown gaea:gaea gaea")
#     # ssh("chmod u+x gaea")
#     ssh("./gaea setup")


def process_out(host):
    def process(line):
        if "?secret=" in line:
            secret = line.partition("=")[2]
            # TODO osx appends a trailing newline (?)
            webbrowser.open(f"https://{host}?secret={secret}")
        print(line, end="", flush=True)

    return process


def setup(digitalocean_token=""):
    """Set up the understory on this system."""
    # TODO ensure in home directory
    print("setting up base system..")
    gaea = Gaea()
    gaea.upgrade_system()
    gaea.setup_firewall()
    # XXX sh.sudo("/etc/init.d/redis-server", "stop")
    # XXX sh.sudo("systemctl", "disable", "redis")
    gaea.etc_dir.mkdir(parents=True, exist_ok=True)
    gaea.src_dir.mkdir(parents=True, exist_ok=True)
    gaea.working_dir.mkdir(parents=True, exist_ok=True)
    gaea.setup_python()
    gaea.setup_nginx()
    gaea.setup_supervisor()
    gaea.setup_gaea(digitalocean_token)
    gaea.setup_tor()
    gaea.setup_firefox()
    gaea.setup_torbrowser()
    gaea.setup_geckodriver()


def get_statuses():
    statuses = {}
    for line in sh.sudo("supervisorctl", "status"):
        if "STARTING" in str(line):
            time.sleep(0.5)
            continue
        try:
            app, status, _, pid = line.split()[:4]
        except ValueError:
            print(f"Can't parse statuses: {line}")
            break
        uptime = line.partition(" uptime ")[2]
        statuses[app.replace("-", ":")] = status, pid, uptime
    return statuses


def log(*args, **kwargs):
    """Print with a prefixed elapsed time indicator."""
    if STARTED:
        total_seconds = int(time.time() - STARTED)
        minutes = int(total_seconds / 60)
        seconds = total_seconds % 60
        print(f"{minutes: 3d}:{seconds:02d}", *args, **kwargs)
    else:
        print(*args, **kwargs)


def get_ip():
    return sh.hostname("-I").split()[0]


def install_app(app, home_dir, github_token):
    if app.startswith("https://"):  # Git repo
        pass  # TODO
    elif "/" in app:  # GitHub project
        working_dir = pathlib.Path(home_dir) / "working"
        user, _, repo = app.partition("/")
        sh.mkdir(working_dir / user, "-p")
        sh.git("clone", f"https://github.com/{app}.git", _cwd=working_dir / user)
        sh.Command(f"{home_dir}/.local/bin/poetry")(
            "install",
            _cwd=working_dir / user / repo,
            _env={},  # NOTE ensures VIRTUAL_ENV is absent
        )
        # XXX gh_prefix = f"https://api.github.com/repos/{app}/releases"
        # XXX gh_token_header = f"token {github_token}"
        # XXX gh_headers = {
        # XXX     "Accept": "application/vnd.github.v3+json",
        # XXX     "Authorization": gh_token_header,
        # XXX }
        # XXX asset = web.get(f"{gh_prefix}/latest",
        # XXX                 headers=gh_headers).json["assets"][0]
        # XXX sh.wget(
        # XXX     f"{gh_prefix}/assets/{asset['id']}",
        # XXX     "-O",
        # XXX     asset["name"],
        # XXX     "--header",
        # XXX     "Accept: application/octet-stream",
        # XXX     "--header",
        # XXX     f"Authorization: {gh_token_header}",
        # XXX     _cwd=home_dir,
        # XXX )
        # XXX sh.sh(
        # XXX     "runinenv",
        # XXX     "system/env",
        # XXX     "pip",
        # XXX     "install",
        # XXX     # TODO "--index-url",
        # XXX     # TODO "",
        # XXX     # TODO "--extra-index-url",
        # XXX     # TODO "",
        # XXX     asset["name"],
        # XXX     _cwd=home_dir,
        # XXX )
    else:  # PyPI package
        sh.sh(
            "runinenv",
            "system/env",
            "pip",
            "install",
            # TODO "--index-url",
            # TODO "",
            # TODO "--extra-index-url",
            # TODO "",
            app,
            _cwd=home_dir,
        )
    sh.sudo("supervisorctl", "restart", "gaea-app", "gaea-app-jobs")


def upgrade_app(app, home_dir):
    sh.sh("runinenv", "system/env", "pip", "install", "-U", app, _cwd=home_dir)
    sh.sudo("supervisorctl", "restart", "gaea-app")


class Gaea:
    """The host of the machine."""

    # TODO home_dir is only used for config and runinenv.. move these
    def __init__(self, home_dir="/home/gaea"):
        """Return the gaea found in `home_dir`."""
        self.home_dir = pathlib.Path(home_dir)
        self.apps_dir = self.home_dir / "apps"
        self.sites_dir = self.home_dir / "sites"
        self.working_dir = self.home_dir / "working"
        self.system_dir = self.home_dir / "system"
        self.bin_dir = self.system_dir / "bin"
        self.env_dir = self.system_dir / "env"
        self.etc_dir = self.system_dir / "etc"
        self.src_dir = self.system_dir / "src"
        self.var_dir = self.system_dir / "var"
        self.nginx_dir = self.system_dir / "nginx"

    def upgrade_system(self):
        """Upgrade aptitude and install new system-level dependencies."""
        apt = sh.sudo.bake(
            "apt", _env=dict(os.environ, DEBIAN_FRONTEND="noninteractive")
        )

        def run_apt(message, *commands):
            log(" ", message)
            while True:
                try:
                    apt(*commands)
                    break
                except sh.ErrorReturnCode_100:
                    # wait for aptitude to unlock
                    time.sleep(1)

        log("configuring system")
        run_apt("updating", "update")
        run_apt("upgrading", "dist-upgrade", "-yq")
        run_apt("installing packages", "install", "-yq", *APTITUDE_PACKAGES)

    def setup_firewall(self):
        """Wall off everything but SSH and web."""
        allow = sh.sudo.bake("ufw", "allow", "proto", "tcp", "from", "any", "to", "any")
        allow.port("22")
        allow.port("80,443")
        sh.sudo("ufw", "--force", "enable")

    def setup_python(self):
        """
        Install Python (w/ SQLite extensions).

        Additionally create a virtual environment and the web package.

        """

        def get_python_sh():
            py_major_version = f"python{VERSIONS['python'].rpartition('.')[0]}"
            return sh.Command(str(self.bin_dir / py_major_version))

        try:
            get_python_sh()
        except sh.CommandNotFound:
            _version = VERSIONS["python"]
            self._build(
                f"python.org/ftp/python/{_version}/Python-{_version}" f".tar.xz",
                "--enable-loadable-sqlite-extensions",
                f"--prefix={self.system_dir}",
            )

        if self.env_dir.exists():
            return
        log("creating primary virtual environment")
        get_python_sh()("-m", "venv", self.env_dir)
        sh.echo(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                VENV=$1
                . ${VENV}/bin/activate
                shift 1
                exec "$@"
                deactivate"""
            ),
            _out=f"{self.home_dir}/runinenv",
        )
        sh.chmod("+x", self.home_dir / "runinenv")

        # sh.sh(self.home_dir / "runinenv", self.env_dir, "pip", "install", "sh==1.11")

        # log("installing SQLite")
        # log(" ", "downloading")
        # sh.wget("https://www.sqlite.org/src/tarball/sqlite.tar.gz", _cwd=self.src_dir)
        # log(" ", "extracting")
        # sh.tar("xf", "sqlite.tar.gz", _cwd=self.src_dir)
        # sqlite_dir = self.src_dir / "sqlite"
        # log(" ", "configuring")
        # sh.bash("./configure", _cwd=sqlite_dir)
        # sh.make("sqlite3.c", _cwd=sqlite_dir)
        # sh.git("clone", "https://github.com/coleifer/pysqlite3", _cwd=self.src_dir)
        # pysqlite_dir = self.src_dir / "pysqlite3"
        # sh.cp(sqlite_dir / "sqlite3.c", ".", _cwd=pysqlite_dir)
        # sh.cp(sqlite_dir / "sqlite3.h", ".", _cwd=pysqlite_dir)
        # sh.sh(
        #     self.home_dir / "runinenv",
        #     self.env_dir,
        #     "python",
        #     "setup.py",
        #     "build_static",
        #     _cwd=pysqlite_dir,
        # )
        # sh.sh(
        #     self.home_dir / "runinenv",
        #     self.env_dir,
        #     "python",
        #     "setup.py",
        #     "install",
        #     _cwd=pysqlite_dir,
        # )

        log("installing Gaea")
        sh.sh(
            self.home_dir / "runinenv",
            self.env_dir,
            "pip",
            "install",
            "libgaea",
        )

        log("installing Poetry")
        get_python_sh()(
            sh.wget(
                "https://raw.githubusercontent.com/python-poetry/poetry"
                "/master/install-poetry.py",
                "-q",
                "-O",
                "-",
            ),
            "-",
        )

    def setup_nginx(self):
        """Install Nginx (w/ TLS, HTTPv2, RTMP) for web serving."""
        nginx_src = f"nginx-{VERSIONS['nginx']}"
        if (self.src_dir / nginx_src).exists():
            return
        sh.wget(
            "https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/"
            "archive/dev.zip",
            "-O",
            "nginx-rtmp-module.zip",
            _cwd=self.src_dir,
        )
        sh.unzip("-qq", "nginx-rtmp-module.zip", _cwd=self.src_dir)
        self._build(
            f"nginx.org/download/{nginx_src}.tar.gz",
            "--with-http_ssl_module",
            "--with-http_v2_module",
            f"--add-module={self.src_dir}/nginx-rtmp-module-dev",
            f"--prefix={self.nginx_dir}",
        )
        sh.mkdir("-p", self.nginx_dir / "conf/conf.d")
        if not (self.nginx_dir / "conf/dhparam.pem").exists():
            self.generate_dhparam()
        with (self.nginx_dir / "conf/nginx.conf").open("w") as fp:
            fp.write(nginx_conf)

    def generate_dhparam(self):
        """
        Generate a unique Diffie-Hellman prime for Nginx.

        This functionality has been abstracted here in order to allow an
        administrator to regenerate a cloned system's dhparam.

        """
        log("generating a large prime for TLS..")
        sh.openssl("dhparam", "-out", self.nginx_dir / "conf/dhparam.pem", DHPARAM_BITS)

    def setup_supervisor(self):
        """Initialize a supervisor configuration."""
        supervisor = configparser.ConfigParser()
        supervisor["program:nginx"] = {
            "autostart": "true",
            "command": (self.nginx_dir / "sbin/nginx"),
            "stopsignal": "INT",
            "user": "root",
        }

        # XXX command = (f"{self.home_dir}/runinenv {self.env_dir} "
        # XXX            f"loveliness serve")
        # XXX supervisor["program:gaea-jobs"] = {"autostart": "true",
        # XXX                                     "command": command,
        # XXX                                     "directory": (self.apps_dir /
        # XXX                                                   "gaea-app"),
        # XXX                                     "stopsignal": "INT",
        # XXX                                     "user": "gaea"}

        # TODO supervisor[f"program:tor"] = {"autostart": "true",
        # TODO                               "command": bin_dir / "tor",
        # TODO                               "stopsignal": "INT",
        # TODO                               "user": "gaea"}
        self._write_supervisor_conf("servers", supervisor)

    def setup_gaea(self, digitalocean_token=""):
        """Set up the gaea web app."""
        ip = sh.hostname("-I").split()[0]
        secret = "".join(
            random.choice("abcdefghjknprstuvxyz23456789") for _ in range(6)
        )
        gaea_app = "gaea.__web__:app"
        site_dir = self.sites_dir / ip
        site_dir.mkdir(parents=True, exist_ok=True)

        # use self-signed certificate as Let's Encrypt does not support IPs
        domain_cnf = configparser.ConfigParser()
        domain_cnf.optionxform = str
        domain_cnf["req"] = {
            "distinguished_name": "req_distinguished_name",
            "prompt": "no",
        }
        domain_cnf["req_distinguished_name"] = {
            "countryName": "XX",
            "stateOrProvinceName": "N/A",
            "localityName": "N/A",
            "organizationName": "self-signed",
            "commonName": f"{ip}: self-signed",
        }
        with (site_dir / "domain.cnf").open("w") as fp:
            domain_cnf.write(fp)
        sh.openssl(
            "req",
            "-x509",
            "-nodes",
            "-days",
            "365",
            "-newkey",
            "rsa:2048",
            "-keyout",
            site_dir / "domain.key",
            "-out",
            site_dir / "domain.crt",
            "-config",
            site_dir / "domain.cnf",
        )

        self.save_config(
            {
                "secret": secret,
                "tokens": {
                    "digitalocean": digitalocean_token,
                    "dynadot": "",
                    "github": "",
                },
                "websites": {},
            }
        )
        self.mount_site(ip, gaea_app)
        print()
        print("You may now sign in to your host while installation continues:")
        print(f"    https://{ip}?secret={secret}")
        print()

    def setup_tor(self):
        """Install Tor for anonymous hosting."""
        tor_dir = f"tor-{VERSIONS['tor']}"
        if (self.src_dir / tor_dir).exists():
            return
        self._build(
            f"dist.torproject.org/{tor_dir}.tar.gz", f"--prefix={self.system_dir}"
        )
        sh.mkdir("-p", self.var_dir / "tor")

    def setup_firefox(self):
        """Install Firefox for web browsing."""
        firefox_dir = f"firefox-{VERSIONS['firefox']}"
        if (self.src_dir / firefox_dir).exists():
            return
        log(f"installing firefox-{VERSIONS['firefox']}")
        sh.wget(
            f"https://archive.mozilla.org/pub/firefox/releases"
            f"/{VERSIONS['firefox']}/linux-x86_64/en-US"
            f"/{firefox_dir}.tar.bz2",
            _cwd=self.src_dir,
        )
        sh.tar("xf", f"{firefox_dir}.tar.bz2", _cwd=self.src_dir)
        sh.mv("firefox", firefox_dir, _cwd=self.src_dir)
        sh.ln("-s", self.src_dir / firefox_dir / "firefox", self.bin_dir)

    def setup_torbrowser(self):  # TODO
        """Install Tor Browser for web browsing over Tor."""

    def setup_geckodriver(self):
        """Install geckodriver for driving gecko-based browsers."""
        geckodriver_dir = f"geckodriver-v{VERSIONS['geckodriver']}-linux64"
        if (self.src_dir / geckodriver_dir).exists():
            return
        log(f"installing geckodriver-{VERSIONS['geckodriver']}")
        sh.wget(
            f"https://github.com/mozilla/geckodriver/releases/download"
            f"/v{VERSIONS['geckodriver']}/{geckodriver_dir}.tar.gz",
            _cwd=self.src_dir,
        )
        sh.tar("xf", f"{geckodriver_dir}.tar.gz", _cwd=self.src_dir)
        sh.mkdir("-p", geckodriver_dir, _cwd=self.src_dir)
        sh.mv("geckodriver", geckodriver_dir, _cwd=self.src_dir)
        sh.ln("-s", self.src_dir / geckodriver_dir / "geckodriver", self.bin_dir)

    def mount_site(self, site, app):
        """Instruct Nginx to route requests for `site` to `app`."""
        if app not in get_statuses():
            if "#" in app:
                project, _, app = app.partition("#")
                self.run_development_app(project, app)
                app = f"{project}/{app}"
            else:
                self.run_production_app(app)
        config = self.get_config()
        config["websites"][site] = app
        self.save_config(config)
        with (self.nginx_dir / f"conf/conf.d/{site}-app.conf").open("w") as fp:
            fp.write(
                nginx_site_app_conf.format(
                    site=site, app=app.replace(":", "-"), ssl_ciphers=SSL_CIPHERS
                )
            )
        sh.sudo("supervisorctl", "restart", "nginx")

    def run_development_app(self, project, app, workers=2):
        """Instruct Supervisor to run given `app` using gunicorn."""
        supervisor = configparser.ConfigParser()
        name = app.replace(":", "-")
        app_dir = self.apps_dir / project / name
        app_dir.mkdir(parents=True, exist_ok=True)
        env_dir = sh.Command(f"{self.home_dir}/.local/bin/poetry")(
            "env",
            "info",
            "--path",
            _cwd=self.working_dir / project,
            _env={},  # NOTE ensures VIRTUAL_ENV is absent
        )
        dashed_project = project.replace("/", "-")
        command = (
            f"{self.home_dir}/runinenv {env_dir} gunicorn {app}"
            f" -k gevent -w {workers} --bind unix:{app_dir}/app.sock"
        )
        supervisor[f"program:{dashed_project}-{name}"] = {
            "autostart": "true",
            "command": command,
            "directory": app_dir,
            "environment": "PYTHONUNBUFFERED=1",
            "stopsignal": "INT",
            "user": "gaea",
        }
        command = f"{self.home_dir}/runinenv {env_dir} loveliness serve"
        supervisor[f"program:{dashed_project}-{name}-jobs"] = {
            "autostart": "true",
            "command": command,
            "directory": app_dir,
            "stopsignal": "INT",
            "user": "gaea",
        }
        self._write_supervisor_conf(f"app-{dashed_project}-{name}", supervisor)

    def run_production_app(self, app, workers=2):
        """Instruct Supervisor to run given `app` using gunicorn."""
        supervisor = configparser.ConfigParser()
        name = app.replace(":", "-")
        app_dir = self.apps_dir / name
        app_dir.mkdir(parents=True, exist_ok=True)
        command = (
            f"{self.home_dir}/runinenv {self.env_dir} gunicorn {app}"
            f" -k gevent -w {workers} --bind unix:{app_dir}/app.sock"
        )
        supervisor[f"program:{name}"] = {
            "autostart": "true",
            "command": command,
            "directory": app_dir,
            "environment": "PYTHONUNBUFFERED=1",
            "stopsignal": "INT",
            "user": "gaea",
        }
        command = f"{self.home_dir}/runinenv {self.env_dir} loveliness serve"
        supervisor[f"program:{name}-jobs"] = {
            "autostart": "true",
            "command": command,
            "directory": app_dir,
            "stopsignal": "INT",
            "user": "gaea",
        }
        self._write_supervisor_conf(f"app-{name}", supervisor)

    def _build(self, archive_url, *config_args):
        archive_filename = archive_url.rpartition("/")[2]
        archive_stem = archive_filename
        for ext in (".gz", ".xz", ".bz2", ".tar"):
            if archive_stem.endswith(ext):
                archive_stem = archive_stem[: -len(ext)]
        archive_file = self.src_dir / archive_filename
        archive_dir = self.src_dir / archive_stem
        if not (archive_file.exists() and archive_dir.exists()):
            log(f"installing {archive_stem.capitalize().replace('-', ' ')}")
        if not archive_file.exists():
            log(" ", "downloading")
            tries = 0
            while True:
                try:
                    sh.wget(f"https://{archive_url}", _cwd=self.src_dir)
                except sh.ErrorReturnCode_1:
                    tries += 1
                    if tries == 3:
                        raise  # fail with traceback for bug reporting
                    time.sleep(3)
                    continue
                break
        if not archive_dir.exists():
            log(" ", "extracting")
            sh.tar("xf", archive_filename, _cwd=self.src_dir)
            log(" ", "configuring")
            sh.bash("./configure", *config_args, _cwd=archive_dir)
            log(" ", "making")
            sh.make(_cwd=archive_dir)
            log(" ", "installing")
            sh.make("install", _cwd=archive_dir)

    def _write_supervisor_conf(self, name, config):
        conf = self.etc_dir / f"{name}.conf"
        with conf.open("w") as fp:
            config.write(fp)
        sh.sudo("ln", "-sf", conf.resolve(), f"/etc/supervisor/conf.d/{name}.conf")
        sh.sudo("supervisorctl", "reread")
        sh.sudo("supervisorctl", "update")

    def get_config(self):
        """Return a dictionary containing gaea configuration."""
        config = pathlib.Path(self.home_dir / "config.json")
        try:
            with config.open() as fp:
                config = json.load(fp)
        except FileNotFoundError:
            config = {}
        return config

    def save_config(self, data):
        """Store `data` as gaea configuration."""
        config = pathlib.Path(self.home_dir / "config.json")
        with config.open("w") as fp:
            json.dump(data, fp)


# parser = argparse.ArgumentParser()
# commands = parser.add_subparsers()
# spawn_p = commands.add_parser("spawn", help="spawn sudoer `ghost`")
# spawn_p.set_defaults(command="spawn")
# setup_p = commands.add_parser("setup", help="set up base system")
# setup_p.set_defaults(command="setup")
# setup_p.add_argument("digitalocean_token")
# do_p = commands.add_parser("digitalocean", help="DigitalOcean hosting tools")
# do_p.set_defaults(command="digitalocean")
# do_p.add_argument("token")
# dd_p = commands.add_parser("dynadot", help="Dynadot registrar tools")
# dd_p.set_defaults(command="dynadot")
# dd_p.add_argument("token")
#
# args = parser.parse_args(argv)
# command = getattr(args, "command", "init")
# ghost = Ghost()
# if command == "init":
# elif command == "spawn":
#     ghost.spawn()
# elif command == "setup":
#     ghost.setup(args.digitalocean_token)
# elif command == "clean":
#     pass  # TODO remove files in src_dir and replace with {filename}.sha256
# elif command == "digitalocean":
#     print(DigitalOcean(args.token).get_droplets())
# elif command == "dynadot":
#     print(Dynadot(args.token).list_domain())
# else:
#     print(f"Unknown command {command}")
#     return 1


# # create a modal message box with a single 'Ok' button
# box = QMessageBox()
# box.setWindowTitle('Title')
# box.setText('Text')
# box.exec()
#
#
# # create a modal message box that offers some choices (Yes|No|Cancel)
# box = QMessageBox()
# box.setWindowTitle('Some Message')
# box.setText("Pushing a button will do something.")
# box.setInformativeText("Do you want to push a button?")
# box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
# box.setDefaultButton(QMessageBox.Save)
# result = box.exec()
#
# if result == QMessageBox.Cancel:
#     print('User pressed Cancel')
# elif result == QMessageBox.No:
#     print('User pressed No')
# elif result == QMessageBox.Yes:
#     print('User pressed Yes')

# text, pressed = QInputDialog.getText(window, "Title", "Please type something...")
# if pressed:
#     print(text)
#
# items = ["option 1", "option 2", "option 3", "option 4"]
# choice, pressed = QInputDialog.getItem(
#     window, "Window Title", "Please choose something...", items
# )
# if pressed:
#     print(choice)
#
# filename, _ = QFileDialog.getOpenFileName(
#     None, "Choose a file", "/home", "Image Files (*.png *.jpg *.bmp)"
# )
# print(filename)
#
# directory = QFileDialog.getExistingDirectory(None, "Choose a directory", "/home")
# print(directory)

nginx_conf = """\
daemon            off;
worker_processes  auto;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    types_hash_max_size  2048;
    sendfile             on;
    tcp_nopush           on;
    tcp_nodelay          on;
    keepalive_timeout    65;
    server_tokens        off;

    gzip          on;
    gzip_disable  "msie6";

    access_log  /home/gaea/system/nginx/logs/access.log;
    error_log   /home/gaea/system/nginx/logs/error.log;

    log_format  gaeafmt  '$remote_addr [$time_local] "$request" $status '
                         '$request_time $bytes_sent "$http_referer" '
                         '"$http_user_agent" "$sent_http_set_cookie"';

    include /home/gaea/system/nginx/conf/conf.d/*.conf;
}

rtmp {
    # Define where the HLS files will be written. Viewers will be fetching
    # these files from the browser, so the `location /hls` above points to
    # this folder as well
    hls on;
    hls_path /home/gaea/streaming/hls;
    hls_fragment 5s;

    # Enable recording archived files of each stream
    # Does not need to be publicly accessible, will convert and publish later
    record all;
    record_path /home/gaea/streaming/rec;
    record_suffix _%Y-%m-%d_%H-%M-%S.flv;
    record_lock on;

    # Define the two scripts that will run when recording starts and when
    # it finishes
    exec_publish /home/gaea/streaming/publish.sh;
    exec_record_done /home/gaea/streaming/finished.sh $path $basename.mp4;

    access_log /home/gaea/system/nginx/logs/rtmp_access.log combined;
    access_log on;

    server {
        listen 1935;
        chunk_size 4096;

        application rtmp {
            live on;
            record all;
        }
    }
}"""

nginx_site_app_conf = """
server {{
    listen       443  ssl  http2;
    listen       [::]:443  ssl  http2;
    server_name  {site};

    ssl_certificate            /home/gaea/sites/{site}/domain.crt;
    ssl_certificate_key        /home/gaea/sites/{site}/domain.key;
    ssl_protocols              TLSv1.3;
    ssl_prefer_server_ciphers  off;
    ssl_ciphers                {ssl_ciphers};
    ssl_session_cache          shared:SSL:10m;
    ssl_session_timeout        1d;
    ssl_dhparam                /home/gaea/system/nginx/conf/dhparam.pem;
    ssl_ecdh_curve             secp384r1;
    ssl_session_tickets        off;
    ssl_stapling               on;
    ssl_stapling_verify        on;
    resolver                   8.8.8.8  8.8.4.4  valid=300s;  # TODO !google
    resolver_timeout           5s;

    charset     utf-8;
    add_header  X-Powered-By  "canopy";
    add_header  X-Frame-Options  "SAMEORIGIN";
    add_header  X-Content-Type-Options  "nosniff";

    # TODO security headers
    # add_header  Strict-Transport-Security  "max-age=15768000"  always;
    # add_header  Strict-Transport-Security
    #             "max-age=63072000; includeSubDomains; preload";
    # add_header  X-Frame-Options  DENY;
    # add_header  X-XSS-Protection  "1; mode=block";
    # add_header  Content-Security-Policy  "require-sri-for script style;"

    client_max_body_size  100M;
    error_page            403 404          /error/40x.html;
    error_page            500 502 503 504  /error/50x.html;
    access_log            /home/gaea/apps/{app}/access.log  gaeafmt;
    error_log             /home/gaea/apps/{app}/error.log   info;

    # TODO: error and static Nginx locations
    # location  /error/  {{
    #     internal;
    #     alias  ../canopy/;
    # }}
    # location  /static/  {{
    #     add_header  Access-Control-Allow-Origin  *;
    #     root  ../canopy/__web__;
    # }}

    location /X/ {{
        internal;
        alias  /home/gaea/apps/{app}/;
    }}

    location  /  {{
        proxy_set_header  X-Forwarded-Proto  $scheme;
        proxy_set_header  Host  $http_host;
        proxy_set_header  X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_redirect  off;
        proxy_pass  http://unix:/home/gaea/apps/{app}/app.sock;

        # XXX uwsgi_param  Host  $http_host;
        # XXX uwsgi_param  X-Real-IP  $remote_addr;
        # XXX uwsgi_param  X-Forwarded-For  $proxy_add_x_forwarded_for;
        # XXX uwsgi_max_temp_file_size  0;
        # XXX uwsgi_pass  unix:/home/gaea/apps/{app}/app.sock;
        # XXX include  /home/gaea/system/nginx/conf/uwsgi_params;
    }}
}}"""
