import os
from pathlib import Path


class CATCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args:
            error_msg = "cat: missing file operand"
            print(error_msg)
            self.logger.error(error_msg)
            return

        for file_path in args:
            try:
                if not os.path.isabs(file_path):
                    file_path = os.path.join(os.getcwd(), file_path)

                if not os.path.exists(file_path):
                    error_msg = f"cat: {file_path}: No such file or directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    continue

                if os.path.isdir(file_path):
                    error_msg = f"cat: {file_path}: Is a directory"
                    print(error_msg)
                    self.logger.error(error_msg)
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    print(content, end='')

                self.logger.info(f"cat: displayed content of {file_path}")

            except PermissionError:
                error_msg = f"cat: {file_path}: Permission denied"
                print(error_msg)
                self.logger.error(error_msg)
            except UnicodeDecodeError:
                error_msg = f"cat: {file_path}: Binary file not supported"
                print(error_msg)
                self.logger.error(error_msg)
            except Exception as e:
                error_msg = f"cat: {file_path}: unexpected error: {str(e)}"
                print(error_msg)
                self.logger.error(error_msg)