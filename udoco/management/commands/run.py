import os
import subprocess
import atexit
import signal

from django.contrib.staticfiles.management.commands.runserver import Command\
    as StaticfilesRunserverCommand


class Command(StaticfilesRunserverCommand):

    def inner_run(self, *args, **options):
        self.start_grunt()
        return super(Command, self).inner_run(*args, **options)

    def start_grunt(self):
        self.grunt_process = subprocess.Popen(
            ['npm run watch'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        atexit.register(os.kill, self.grunt_process.pid, signal.SIGTERM)
