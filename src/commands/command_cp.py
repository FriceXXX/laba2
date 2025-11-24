import os
import shutil
from pathlib import Path


class CPCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args or len(args) < 2:
            error_msg = "cp: missing file operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: cp [-r] <source> <destination>")
            return

        recursive = False
        sources = []
        destination = None

        for arg in args:
            if arg == '-r':
                recursive = True
            else:
                if destination is None and sources:
                    destination = arg
                else:
                    sources.append(arg)

        if len(sources) < 1 or destination is None:
            error_msg = "cp: missing file operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: cp [-r] <source> <destination>")
            return

        try:
            destination = self._resolve_path(destination)

            if len(sources) > 1:
                if not os.path.exists(destination):
                    error_msg = f"cp: target '{destination}' is not a directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    return

                if not os.path.isdir(destination):
                    error_msg = f"cp: target '{destination}' is not a directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    return

            for source in sources:
                source_path = self._resolve_path(source)
                self._copy_item(source_path, destination, recursive)

        except Exception as e:
            error_msg = f"cp: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _copy_item(self, source, destination, recursive):
        if not os.path.exists(source):
            error_msg = f"cp: cannot stat '{source}': No such file or directory"
            print(error_msg)
            self.logger.error(error_msg)
            return

        if os.path.isdir(destination) and not destination.endswith('/'):
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            dest_path = destination

        try:
            if os.path.isdir(source):
                if not recursive:
                    error_msg = f"cp: -r not specified; omitting directory '{source}'"
                    print(error_msg)
                    self.logger.error(error_msg)
                    return

                shutil.copytree(source, dest_path)
                self.logger.info(f"cp: copied directory '{source}' to '{dest_path}'")
                print(f"Copied directory '{source}' to '{dest_path}'")

            else:
                shutil.copy2(source, dest_path)
                self.logger.info(f"cp: copied file '{source}' to '{dest_path}'")
                print(f"Copied file '{source}' to '{dest_path}'")

        except PermissionError:
            error_msg = f"cp: cannot copy '{source}': Permission denied"
            print(error_msg)
            self.logger.error(error_msg)
        except FileExistsError:
            error_msg = f"cp: cannot copy '{source}': Destination already exists"
            print(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"cp: cannot copy '{source}': {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)