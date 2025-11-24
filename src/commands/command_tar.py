import os
import tarfile
import gzip
from pathlib import Path


class TarCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args or len(args) < 2:
            error_msg = "tar: missing operands"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: tar <folder> <archive.tar.gz>")
            return

        folder = args[0]
        archive_name = args[1]

        if not archive_name.endswith('.tar.gz') and not archive_name.endswith('.tgz'):
            archive_name += '.tar.gz'

        try:
            folder_path = self._resolve_path(folder)
            archive_path = self._resolve_path(archive_name)

            if not os.path.exists(folder_path):
                error_msg = f"tar: cannot stat '{folder}': No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if not os.path.isdir(folder_path):
                error_msg = f"tar: '{folder}' is not a directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            self._create_tar_archive(folder_path, archive_path)
            print(f"Created tar archive: {archive_path}")
            self.logger.info(f"tar: created archive '{archive_path}' from '{folder_path}'")

        except Exception as e:
            error_msg = f"tar: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _create_tar_archive(self, folder_path, archive_path):
        with tarfile.open(archive_path, 'w:gz') as tar:
            # Добавляем всю папку в архив
            tar.add(folder_path, arcname=os.path.basename(folder_path))


class UntarCommand:
    def __init__(self, logger):
        self.logger = logger

    def execute(self, args=None):
        if not args:
            error_msg = "untar: missing operand"
            print(error_msg)
            self.logger.error(error_msg)
            print("Usage: untar <archive.tar.gz> [destination]")
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
                error_msg = f"untar: cannot open '{archive}': No such file or directory"
                print(error_msg)
                self.logger.error(error_msg)
                return

            if not tarfile.is_tarfile(archive_path):
                error_msg = f"untar: '{archive}' is not a tar file"
                print(error_msg)
                self.logger.error(error_msg)
                return

            self._extract_tar_archive(archive_path, dest_path)
            print(f"Extracted tar archive to: {dest_path}")
            self.logger.info(f"untar: extracted '{archive_path}' to '{dest_path}'")

        except Exception as e:
            error_msg = f"untar: unexpected error: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(os.getcwd(), path))

    def _extract_tar_archive(self, archive_path, dest_path):
        # Создаем папку назначения если не существует
        os.makedirs(dest_path, exist_ok=True)

        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()

            tar.extractall(dest_path)

            print(f"Extracted {len(members)} files/directories:")
            for member in members:
                print(f"  {member.name} ({'directory' if member.isdir() else 'file'})")

