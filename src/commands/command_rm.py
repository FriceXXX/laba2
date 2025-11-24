import os
import shutil


class RMCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args:
            error_msg = "rm: missing operand"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: rm [-r] <file1> [file2 ...]")
            return

        recursive = False
        targets = []

        for arg in args:
            if arg == '-r':
                recursive = True
            else:
                targets.append(arg)

        if not targets:
            error_msg = "rm: missing operand"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: rm [-r] <file1> [file2 ...]")
            return

        for target in targets:
            target_path = self._resolve_path(target)
            self._remove_item(target_path, recursive)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _remove_item(self, target, recursive):
        if not os.path.exists(target):
            error_msg = f"rm: cannot remove '{target}': No such file or directory"
            print(error_msg)
            self.logger.error(error_msg)
            return

        if self._is_protected_directory(target):
            error_msg = f"rm: cannot remove '{target}': Operation not permitted"
            print(error_msg)
            self.logger.error(error_msg)
            return

        try:
            if os.path.isdir(target):
                if not recursive:
                    error_msg = f"rm: cannot remove '{target}': Is a directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    return

                response = input(f"rm: remove directory '{target}' recursively? (y/n) ")
                if response.lower() not in ['y', 'yes']:
                    print("rm: cancellation confirmed")
                    return

                shutil.rmtree(target)
                self.logger.info(f"rm: removed directory '{target}'")
                print(f"Removed directory '{target}'")

            else:
                os.remove(target)
                self.logger.info(f"rm: removed file '{target}'")
                print(f"Removed file '{target}'")

        except PermissionError:
            error_msg = f"rm: cannot remove '{target}': Permission denied"
            print(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"rm: cannot remove '{target}': {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _is_protected_directory(self, path):
        protected_paths = [
            '/',
            '/root',
            '/home',
            '/etc',
            '/bin',
            '/sbin',
            '/usr',
            '/var',
            '/sys',
            '/proc',
            '/dev'
        ]

        real_path = os.path.realpath(path)

        if real_path in ['/', '..', '../..'] or real_path.endswith('/..'):
            return True

        for protected in protected_paths:
            if real_path == protected or real_path.startswith(protected + '/'):
                return True

        return False