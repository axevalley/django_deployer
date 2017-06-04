"""This module contains wrappers for directories."""


from fabric.api import run


class Directory:
    """Provides methods for working with directories."""

    def __init__(self, deployment, name):
        """Get absolute path to directory."""
        self.deployment = deployment
        self.name = name
        self.full_path = deployment.expanduser(
            deployment.join(name))
        self.deployment.directories.append(self)

    def __str__(self):
        return str(self.full_path)

    def create(self):
        """Create directory on server."""
        run('mkdir -p {}'.format(self.full_path))

    def join(self, directory):
        """Return new Directory object representing a sub directory of self."""
        return Directory(
            self.deployment, self.deployment.join(self.full_path, directory))


class RootDirectory(Directory):
    """Container for project root directory."""

    def __init__(self, deployment, name):
        """Get absolute path to directory."""
        self.deployment = deployment
        self.name = name
        self.full_path = deployment.expanduser(name)
        self.deployment.directories.append(self)


class UserDirectory(RootDirectory):
    """Container for user home directory."""

    def __init__(self, deployment, name):
        """Get absolute path to directory."""
        self.deployment = deployment
        self.name = name
        self.full_path = '/home/{}'.format(name)
