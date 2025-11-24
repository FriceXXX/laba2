import os
import stat
import time
from pathlib import Path


class LSCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        path = None
        detailed = False

        if args:
            for arg in args:
                if arg == '-l':
                    detailed = True
                elif not arg.startswith('-'):
                    path = arg

        if path is None:
            path = os.getcwd()
        else:
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)

        try:
            if not os.path.exists(path):
                error_msg = f"ls: {path}: No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if os.path.isfile(path):
                self._display_item(path, path, detailed)
            else:
                items = os.listdir(path)
                items.sort()

                for item in items:
                    item_path = os.path.join(path, item)
                    self._display_item(item, item_path, detailed)

        except PermissionError:
            error_msg = f"ls: {path}: Permission denied"
            print(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"ls: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _display_item(self, name, full_path, detailed):
        if detailed:
            try:
                file_stat = os.stat(full_path)

                permissions = self._get_permissions(file_stat.st_mode)

                size = file_stat.st_size

                mod_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                         time.localtime(file_stat.st_mtime))

                item_type = 'd' if os.path.isdir(full_path) else '-'

                print(f"{item_type}{permissions} {size:8} {mod_time} {name}")

            except Exception as e:
                print(f"?????????? ???? ????-??-?? ??:??:?? {name}")
        else:
            print(name)

    def _get_permissions(self, mode):
        permissions = []

        # user
        permissions.append('r' if mode & stat.S_IRUSR else '-')
        permissions.append('w' if mode & stat.S_IWUSR else '-')
        permissions.append('x' if mode & stat.S_IXUSR else '-')

        # group
        permissions.append('r' if mode & stat.S_IRGRP else '-')
        permissions.append('w' if mode & stat.S_IWGRP else '-')
        permissions.append('x' if mode & stat.S_IXGRP else '-')

        # othera
        permissions.append('r' if mode & stat.S_IROTH else '-')
        permissions.append('w' if mode & stat.S_IWOTH else '-')
        permissions.append('x' if mode & stat.S_IXOTH else '-')

        return ''.join(permissions)