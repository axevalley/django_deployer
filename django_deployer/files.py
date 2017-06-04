"""This module contains wrappers for files."""

import random

from fabric.contrib.files import append, sed


class File:
    """Base class for files."""

    def __init__(self, deployment, directory, name):  # noqa
        self.deployment = deployment
        self.directory = directory
        self.name = name
        self.path = str(self.deployment.join(self.directory, self.name))

    def touch(self):
        """Create file on server."""
        self.deployment.touch(self.path)

    def append(self, text):
        """Add text to file."""
        append(self.path, text)

    def sed(self, find, replace):
        """Find and replace in file."""
        sed(self.path, str(find), str(replace))


class ProjectFile(File):
    """File in main project directory."""

    def __init__(self, deployment):  # noqa
        self.deployment = deployment
        self.directory = self.deployment.source_directory.join(
            self.deployment.project_name)
        self.path = str(self.deployment.join(self.directory, self.name))


class RequirementsFile(File):
    """Pip requirements file."""

    name = 'requirements.txt'

    def __init__(self, deployment):  # noqa
        self.deployment = deployment
        self.directory = self.deployment.source_directory.join(
            self.deployment.project_name)
        self.path = str(self.deployment.source_directory)


class SettingsFile(ProjectFile):
    """File for django settings file."""

    name = 'settings.py'

    def update(self):
        """Replace local settings with server settings."""
        self.sed("DEBUG = True", "DEBUG = False")
        self.sed(
            'ALLOWED_HOSTS =.+$',
            'ALLOWED_HOSTS = ["{}"]'.format(self.env.host))
        self.append('\nfrom . secret_key import SECRET_KEY')


class SecretKeyFile(ProjectFile):
    """File containing django secret key."""

    name = 'secret_key.py'
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!"@#$%^&*"'

    def __init__(self, deployment):  # noqa
        self.deployment = deployment
        self.directory = self.deployment.source_directory.join(
            self.deployment.project_name)
        self.path = str(self.deployment.join(self.directory, self.name))

    def get_key(self):
        """Generate new secret key."""
        return ''.join(
            [random.SystemRandom().choice(self.chars) for _ in range(50)])

    def create(self):
        """Create secret_key.py on server."""
        self.touch()
        key = self.get_key()
        self.append("SECRET_KEY = '{}'".format(key))


class DjangoManagement(ProjectFile):
    """File for django settings file."""

    name = 'manage.py'

    def execute(self, command):
        """Run manage.py command."""
        self.deployment.execute_python('{} {}'.format(self.path, command))
