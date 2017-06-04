from fabric.api import run


class PythonEnv:

    system_python = 'python3'

    def __init__(self, deployment):
        self.directory = self.deployment.virtualenv_directory
        self.bin = self.join('bin')
        self.executable = self.deployment.join(self.bin, 'python')
        self.pip = self.deployment.join(self.bin, 'pip')

    def execute_python(self, command):
        run('{} {}'.format(self.executable, command))

    def execute_pip(self, command):
        run('{} {}'.format(self.pip, command))

    def create(self):
        run('{} -m venv {}'.format(self.system_python, str(self.directory)))

    def update_packages(self):
        self.execute_pip(
            'install -r {}'.format(self.deployment.requirements_file))
