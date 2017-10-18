import os
import subprocess
import atexit
import signal

from django.contrib.staticfiles.management.commands.runserver import Command\
    as StaticfilesRunserverCommand


class Command(StaticfilesRunserverCommand):

    def inner_run(self, *args, **options):
        self.start_frontend()
        return super(Command, self).inner_run(*args, **options)

    def start_frontend(self):
        self._process = subprocess.Popen(
            ['cd frontend && npm run watch integrate'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        atexit.register(os.kill, self._process.pid, signal.SIGTERM)
