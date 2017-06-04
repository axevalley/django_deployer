"""Deployment class."""

from fabric.contrib.files import append, exists, sed  # noqa
from fabric.api import env, local, run, put  # noqa
from fabric.operations import sudo  # noqa
from fabric.context_managers import cd

from . directory import RootDirectory, UserDirectory
from . import files
from . pythonenv import PythonEnv


class Deployment:
    """Base class for django deployments."""

    root_directory = '~/sites'
    url = None
    project_name = None
    repo = None
    directories = []
    cd = cd

    def __init__(self):  # noqa
        self.env = env
        if self.url is None:
            self.url = env.host
        self.get_directories()
        self.settings_file = files.SettingsFile(self)
        self.secret_key_file = files.SecretKeyFile(self)
        self.requirements_file = files.RequirementsFile(self)
        self.python_env = PythonEnv(self)
        self.management = files.DjangoManagement(self)

    def copy_server_settings_file(self):
        """Copy server_settings.py to server."""
        put(
            self.server_settings_path,
            str(self.source_directory.join(self.project_name)))

    def join(self, *directories, seperator='/'):
        """Create a filepath from a list of strings."""
        return seperator.join([str(directory) for directory in directories])

    def expanduser(self, path):
        """Expand filpaths using ~ to full absolute path."""
        return path.replace('~', str(self.user_directory))

    def get_directories(self):
        """Create Directory objects for necessary directories."""
        self.user_directory = UserDirectory(self, env.user)
        self.full_root = RootDirectory(self, self.root_directory)
        self.project_directory = self.full_root.join(self.url)
        self.source_directory = self.project_directory.join('source')
        self.virtualenv_directory = self.project_directory.join('virtualenv')
        self.static_directory = self.project_directory.join('static')

    def cd(self, directory):
        """Execute a change directory command on server."""
        run('cd {}'.format(str(directory)))

    def touch(self, filename):
        """Create empty file on server."""
        run('touch {}'.format(str(filename)))

    def make_directories(self):
        """Create all necessary directories on server."""
        for directory in self.directories:
            directory.create()

    def get_local_commit(self):
        """Return current commit of git repo for current working directory."""
        return local("git log -n 1 --format=%H", capture=True)

    def update_source(self, commit=None):
        """Update serverside git repo."""
        if commit is None:
            commit = self.get_local_commit()
        with cd(str(self.source_directory)):
            run('git fetch')
            run('git reset --hard {}'.format(commit))

    def clone_source(self, commit=None):
        """Clone repo to source directory."""
        if commit is None:
            commit = self.get_local_commit()
        run('git clone {} {}'.format(self.repo, str(self.source_directory)))
        with cd(str(self.source_directory)):
            run('git checkout {}'.format(commit))

    def update_static_files(self):
        """Update serverside static files."""
        self.management.execute('collectstatic')

    def migrate_database(self):
        """Create and updates database."""
        self.management.execute('migrate --noinput')

    def restart_server(self):
        """Restart gunicorn process for site."""
        sudo("systemctl restart gunicorn-{}".format(self.url))

    def deploy(self):
        """Deploy project to server."""
        self.make_directories()
        self.clone_source()
        self.secret_key_file.create()
        self.copy_server_settings_file()

    def update(self):
        """Update project on server."""
        self.update_source()
        self.copy_server_settings_file()
