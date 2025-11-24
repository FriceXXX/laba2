import os
import shutil


class MVCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args or len(args) < 2:
            error_msg = "mv: missing file operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: mv <source> <destination>")
            print("       mv <source1> <source2> ... <destination_directory>")
            return

        sources = args[:-1]
        destination = args[-1]

        try:
            destination = self._resolve_path(destination)

            if len(sources) > 1:
                if os.path.exists(destination) and not os.path.isdir(destination):
                    error_msg = f"mv: target '{destination}' is not a directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    return

                if not os.path.exists(destination):
                    os.makedirs(destination)

            for source in sources:
                source_path = self._resolve_path(source)
                self._move_item(source_path, destination)

        except Exception as e:
            error_msg = f"mv: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _move_item(self, source, destination):
        if not os.path.exists(source):
            error_msg = f"mv: cannot stat '{source}': No such file or directory"
            print(error_msg)
            self.logger.error(error_msg)
            return

        if os.path.isdir(destination) and not destination.endswith('/'):
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            dest_path = destination

        if os.path.isdir(source) and dest_path.startswith(source + '/'):
            error_msg = f"mv: cannot move '{source}' to a subdirectory of itself"
            print(error_msg)
            self.logger.error(error_msg)
            return

        try:
            shutil.move(source, dest_path)
            self.logger.info(f"mv: moved '{source}' to '{dest_path}'")
            print(f"Moved '{source}' to '{dest_path}'")

        except PermissionError:
            error_msg = f"mv: cannot move '{source}': Permission denied"
            print(error_msg)
            self.logger.error(error_msg)
        except FileExistsError:
            error_msg = f"mv: cannot move '{source}': Destination already exists"
            print(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"mv: cannot move '{source}': {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)