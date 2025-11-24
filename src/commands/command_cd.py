import os
from pathlib import Path


class CDCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        target_path = None

        if args:
            if len(args) > 1:
                error_msg = "cd: too many arguments"
                print(error_msg)
                self.logger.error(error_msg)
                return
            target_path = args[0]

        if target_path is None:
            target_path = str(Path.home())
        elif target_path == "~":
            target_path = str(Path.home())
        else:
            target_path = self._resolve_path(target_path)

        try:
            if not os.path.isabs(target_path):
                target_path = os.path.join(os.getcwd(), target_path)

            target_path = os.path.normpath(target_path)

            if not os.path.exists(target_path):
                error_msg = f"cd: {target_path}: No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if not os.path.isdir(target_path):
                error_msg = f"cd: {target_path}: Not a directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            os.chdir(target_path)
            # self.logger.info(f"cd: changed directory to {target_path}")

        except PermissionError:
            error_msg = f"cd: {target_path}: Permission denied"
            print(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"cd: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)

        current_dir = os.getcwd()

        if path == "..":
            return os.path.dirname(current_dir)
        elif path.startswith("../"):
            return os.path.normpath(os.path.join(current_dir, path))
        elif path == ".":
            return current_dir
        elif path.startswith("./"):
            return os.path.normpath(os.path.join(current_dir, path[2:]))
        else:
            return os.path.normpath(os.path.join(current_dir, path))