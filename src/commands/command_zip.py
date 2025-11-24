import os
import zipfile
from pathlib import Path


class ZipCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args or len(args) < 2:
            error_msg = "zip: missing operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: zip <folder> <archive.zip>")
            return

        folder = args[0]
        archive_name = args[1]

        if not archive_name.endswith('.zip'):
            archive_name += '.zip'

        try:
            folder_path = self._resolve_path(folder)
            archive_path = self._resolve_path(archive_name)

            if not os.path.exists(folder_path):
                error_msg = f"zip: cannot stat '{folder}': No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if not os.path.isdir(folder_path):
                error_msg = f"zip: '{folder}' is not a directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            self._create_zip_archive(folder_path, archive_path)
            print(f"Created zip archive: {archive_path}")
            self.logger.info(f"zip: created archive '{archive_path}' from '{folder_path}'")

        except Exception as e:
            error_msg = f"zip: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _create_zip_archive(self, folder_path, archive_path):
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)

                    arcname = os.path.relpath(file_path, os.path.dirname(folder_path))

                    zipf.write(file_path, arcname)


class UnzipCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args:
            error_msg = "unzip: missing operand"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: unzip <archive.zip> [destination]")
            return

        archive = args[0]
        destination = args[1] if len(args) > 1 else None

        try:
            archive_path = self._resolve_path(archive)

            if destination:
                dest_path = self._resolve_path(destination)
            else:
                dest_path = os.getcwd()

            if not os.path.exists(archive_path):
                error_msg = f"unzip: cannot open '{archive}': No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if not zipfile.is_zipfile(archive_path):
                error_msg = f"unzip: '{archive}' is not a zip file"
                print(error_msg)
                self.logger.error(error_msg)
                return

            self._extract_zip_archive(archive_path, dest_path)
            print(f"Extracted zip archive to: {dest_path}")
            self.logger.info(f"unzip: extracted '{archive_path}' to '{dest_path}'")

        except Exception as e:
            error_msg = f"unzip: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _extract_zip_archive(self, archive_path, dest_path):
        os.makedirs(dest_path, exist_ok=True)

        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()

            zipf.extractall(dest_path)

            print(f"Extracted {len(file_list)} files/directories:")
            for file in file_list:
                print(f"  {file}")