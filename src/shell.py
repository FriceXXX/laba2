import os
import sys

from src.logger import ShellLogger
from src.commands.command_ls import LSCommand
from src.commands.command_cd import CDCommand
from src.commands.command_cat import CATCommand
from src.commands.command_rm import RMCommand
from src.commands.command_mv import MVCommand
from src.commands.command_cp import CPCommand
from src.commands.command_zip import ZipCommand, UnzipCommand
from src.commands.command_tar import TarCommand, UntarCommand
from src.commands.command_grep import GrepCommand


class PythonShell:
    def __init__(self):
        self.logger = ShellLogger()
        self.commands = {
            'ls': LSCommand(self.logger),
            'cd': CDCommand(self.logger),
            'cat': CATCommand(self.logger),
            'rm': RMCommand(self.logger),
            'cp': CPCommand(self.logger),
            'mv': MVCommand(self.logger),
            'zip': ZipCommand(self.logger),
            'unzip': UnzipCommand(self.logger),
            'tar': TarCommand(self.logger),
            'untar': UntarCommand(self.logger),
            'grep': GrepCommand(self.logger),
        }
        self.running = True

    def get_current_path(self):
        cwd = os.getcwd()
        home = os.path.expanduser("~")

        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]

        return f"\033[92m{os.getenv('USER', 'user')}@pyshell\033[0m:\033[94m{cwd}\033[0m$ "

    def parse(self, user_input):
        if not user_input.strip():
            return None, None

        parts = user_input.strip().split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else None

        return command, args

    def execute_command(self, command, args):
        if command in self.commands:
            self.commands[command].execute(args)
        elif command == 'quit':
            sys.exit()
        else:
            error_msg = f"{command}: command not found"
            print(error_msg)
            self.logger.error(error_msg)

    def run(self):
        while self.running:
            try:
                user_input = input(self.get_current_path())
                command, args = self.parse(user_input)

                if command is None:
                    continue

                self.execute_command(command, args)

            except KeyboardInterrupt:
                sys.exit(0)
            except EOFError:
                self.running = False
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(error_msg)
                self.logger.error(error_msg)

