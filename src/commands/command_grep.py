import os
import re

class GrepCommand:
    def __init__(self, logger):
        self.logger = logger

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))


    def execute(self, args=None):
        if not args or len(args) < 2:
            error_msg = "grep: missing operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: grep [-r] [-i] <pattern> <path>")
            return

        recursive = False
        ignore_case = False
        pattern = None
        path = None

        for arg in args:
            if arg == '-r':
                recursive = True
            elif arg == '-i':
                ignore_case = True
            elif pattern is None:
                pattern = arg
            else:
                path = arg

        if pattern is None or path is None:
            error_msg = "grep: missing pattern or path"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: grep [-r] [-i] <pattern> <path>")
            return

        try:
            search_path = self._resolve_path(path)

            if not os.path.exists(search_path):
                error_msg = f"grep: {search_path}: No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            # убираем учет регистра
            if ignore_case:
                flags = re.IGNORECASE
            else:
                flags = 0
            try:
                pattern_re = re.compile(pattern, flags)
            except re.error as e:
                error_msg = f"grep: invalid pattern: {e}"
                print(error_msg)
                self.logger.error(error_msg)
                return

            matches_found = self._search_pattern(pattern_re, search_path, recursive)

            if not matches_found:
                print("No matches found")

            self.logger.info(f"grep: searched for '{pattern}' in '{search_path}' "
                             f"(recursive: {recursive}, ignore_case: {ignore_case})")

        except Exception as e:
            error_msg = f"grep: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _search_pattern(self, pattern, path, recursive):
        matches_found = False

        if os.path.isfile(path): # поиск в файле
            matches = self._search_in_file(pattern, path)
            if matches:
                matches_found = True
                self._print_matches(path, matches)
        elif recursive == True: # Поиск в директории
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    matches = self._search_in_file(pattern, file_path)
                    if matches:
                        matches_found = True
                        self._print_matches(file_path, matches)

        elif recursive == False:
            print('Is a directory')

        return matches_found



    def _search_in_file(self, pattern, file_path):
        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    clean_line = line.rstrip('\n\r')

                    if pattern.search(clean_line):
                        matches.append((line_num, clean_line))

        except PermissionError:
            print(f"grep: {file_path}: Permission denied")
        except UnicodeDecodeError:
            pass
        except Exception as e:
            print(f"grep: {file_path}: error reading file: {e}")

        return matches

    def _print_matches(self, file_path, matches):
        '''вывод совпадений'''

        relative_path = os.path.relpath(file_path, os.getcwd())
        if relative_path.startswith('../'):
            relative_path = file_path

        for line_num, line_text in matches:
            print(f"{relative_path}:{line_num}:{line_text}")
