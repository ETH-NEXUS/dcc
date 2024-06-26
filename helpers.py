"""
Helpers
====================================
Helper classes and functions
"""

import os
import shlex
from subprocess import run
from enum import Enum
from yachalk import chalk
from rich.console import Console
from rich.table import Table


class ReturnCode(Enum):
    OK = 0


class Executor:
    """
    Class to execute shell commands
    """

    @classmethod
    def success(cls, command: str, env: dict = None) -> bool:
        ret, _ = cls.__run(command, env=env)
        return ret == ReturnCode.OK.value

    @classmethod
    def run(cls, command: str, env: dict = None) -> str:
        _, output = cls.__run(command, env=env)
        return cls.__handle_output(output)

    @classmethod
    def __run(cls, command: str, env: dict = None) -> tuple[int, str]:
        """
        Runs a shell command with the default environment.
        If env is given it is _UPDATED_ to the default environment.
        """
        _env = os.environ.copy()
        if env:
            _env.update(env)
        p = run(shlex.split(command), capture_output=True, env=_env)
        return p.returncode, cls.__handle_output(p.stdout.decode())

    @classmethod
    def __handle_output(cls, output: str) -> str:
        # We remove the last \n
        return output.rstrip("\n")


class Message:
    """
    Class to output colored messages to the console
    """

    @classmethod
    def info(cls, message):
        print(chalk.green_bright.bold(message))

    @classmethod
    def warn(cls, message):
        print(chalk.yellow_bright.bold(message))

    @classmethod
    def error(cls, message):
        print(chalk.red_bright.bold(message))

    @classmethod
    def debug(cls, message):
        print(chalk.blue_bright.bold(message))


class TableOutput:
    """
    Class to output text in table format
    """

    console = Console()

    @classmethod
    def out(
        cls,
        data: str | list,
        sep: str = "#",
        headers: tuple[str] = None,
        show_lines=False,
    ):
        table = Table(
            show_header=(headers is not None), show_lines=show_lines, show_edge=False
        )
        if headers:
            for header in headers:
                table.add_column(header)

        if isinstance(data, str):
            data = data.split("\n")

        for line in data:
            if isinstance(line, str):
                table.add_row(*line.split(sep))
            elif isinstance(line, list):
                table.add_row(*line)

        cls.console.print(table)


####################
# OLD CODE
####################


# class Interactive():
#     """
#     Execute a command interactively with pseudo terminal
#     found at https://stackoverflow.com/questions/41542960/run-interactive-bash-with-popen-and-a-dedicated-tty-python
#     """

#     def __init__(self, command: str = '/bin/bash', env: dict = None):
#         self.command = command
#         self.env = os.environ.copy()
#         if env:
#             self.env.update(env)
#         self.process = None

#     def run(self):
#         old_tty = termios.tcgetattr(sys.stdin)
#         tty.setraw(sys.stdin.fileno())

#         master, slave = pty.openpty()

#         try:
#             self.process = Popen(
#                 shlex.split(self.command),
#                 preexec_fn=os.setsid,
#                 stdin=slave,
#                 stdout=slave,
#                 stderr=slave,
#                 env=self.env)

#             while True:
#                 r, _, _ = select.select([sys.stdin, master], [], [])
#                 if sys.stdin in r:
#                     d = os.read(sys.stdin.fileno(), 10240)
#                     os.write(master, d)
#                 elif master in r:
#                     o = os.read(master, 10240)
#                     if o:
#                         os.write(sys.stdout.fileno(), o)

#                 if self.process.poll() is not None:
#                     sys.stdout.flush()
#                     break
#                 else:
#                     sleep(0.1)

#         finally:
#             # restore tty settings back
#             termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
