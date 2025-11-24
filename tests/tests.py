import os
import sys
from io import StringIO
from unittest.mock import Mock
from pyfakefs.fake_filesystem_unittest import TestCase

# Добавляем путь для импорта модулей
sys.path.append('.')

from src.commands.command_ls import LSCommand
from src.commands.command_cd import CDCommand
from src.commands.command_cat import CATCommand
from src.commands.command_cp import CPCommand
from src.commands.command_rm import RMCommand
from src.commands.command_mv import MVCommand
from src.commands.command_zip import ZipCommand
from src.commands.command_tar import TarCommand
from src.commands.command_zip import UnzipCommand
from src.commands.command_tar import UntarCommand
from src.commands.command_grep import GrepCommand

class TestShellCommands(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.logger = Mock()

        self.fs.create_file('/test/file1.txt', contents='Hello World!')
        self.fs.create_file('/test/file2.txt', contents='Test content')
        self.fs.create_dir('/test/subdir')
        self.fs.create_file('/test/subdir/nested.txt', contents='Nested file')
        self.fs.create_dir('/home/user/documents')

    def normalize_path(self, path):
        return path.replace('\\', '/')

    def capture_output(self, func, *args):
        '''вывод stdout'''
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            func(*args)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_ls_command(self):
        '''тест ls'''
        ls_cmd = LSCommand(self.logger)

        # Простой ls
        output = self.capture_output(ls_cmd.execute, ['/test'])
        self.assertIn('file1.txt', output)
        self.assertIn('file2.txt', output)
        self.assertIn('subdir', output)

        # ls -l
        output = self.capture_output(ls_cmd.execute, ['-l', '/test'])
        self.assertIn('file1.txt', output)


    def test_cd_command(self):
        '''Тест cd'''
        cd_cmd = CDCommand(self.logger)
        original_cwd = os.getcwd()

        try:
            # Переход в существующий каталог
            cd_cmd.execute(['/home/user/documents'])
            current_dir = self.normalize_path(os.getcwd())
            self.assertEqual(current_dir, 'C:/home/user/documents')

            # Переход на уровень выше
            cd_cmd.execute(['..'])
            current_dir = self.normalize_path(os.getcwd())
            self.assertEqual(current_dir, 'C:/home/user')

            # Переход в несуществующий каталог
            output = self.capture_output(cd_cmd.execute, ['/nonexistent'])
            self.assertIn('No such file', output)

        finally:
            os.chdir(original_cwd)

    def test_cat_command(self):
        '''Тест cat'''
        cat_cmd = CATCommand(self.logger)

        # Чтение существующего файла
        output = self.capture_output(cat_cmd.execute, ['/test/file1.txt'])
        self.assertEqual(output, 'Hello World!')

        # Чтение несуществующего файла
        output = self.capture_output(cat_cmd.execute, ['/nonexistent.txt'])
        self.assertIn('No such file', output)

        # Чтение директории вместо файла
        output = self.capture_output(cat_cmd.execute, ['/test/subdir'])
        self.assertIn('Is a directory', output)

    def test_cp_command(self):
        '''Тест cp'''
        cp_cmd = CPCommand(self.logger)

        # Копирование файла
        cp_cmd.execute(['/test/file1.txt', '/copy.txt'])
        self.assertTrue(os.path.exists('/copy.txt'))
        with open('/copy.txt', 'r') as f:
            self.assertEqual(f.read(), 'Hello World!')

        # Копирование несуществующего файла
        output = self.capture_output(cp_cmd.execute, ['/nonexistent.txt', '/dest.txt'])
        self.assertIn('cannot stat', output)

        # Копирование директории без флага -r
        output = self.capture_output(cp_cmd.execute, ['/test/subdir', '/backup'])
        self.assertIn('omitting directory', output)

    def test_rm_command(self):
        '''Тест rm'''
        rm_cmd = RMCommand(self.logger)

        # Удаление файла
        self.fs.create_file('/to_delete.txt')
        rm_cmd.execute(['/to_delete.txt'])
        self.assertFalse(os.path.exists('/to_delete.txt'))

        # Удаление несуществующего файла
        output = self.capture_output(rm_cmd.execute, ['/nonexistent.txt'])
        self.assertIn('cannot remove', output)

        # рекурсивное удаление
        output = self.capture_output(rm_cmd.execute, ['-r', '/test'])
        self.assertIn("rm: remove directory 'C:\\test' recursively? (y/n)", output)

    def test_mv_command(self):
        '''Тест mv'''
        mv_cmd = MVCommand(self.logger)

        # Перемещение файла
        mv_cmd.execute(['/test/file1.txt', '/moved.txt'])
        self.assertFalse(os.path.exists('/test/file1.txt'))
        self.assertTrue(os.path.exists('/moved.txt'))

        # Переименование файла
        self.fs.create_file('/old_name.txt')
        mv_cmd.execute(['/old_name.txt', '/new_name.txt'])
        self.assertFalse(os.path.exists('/old_name.txt'))
        self.assertTrue(os.path.exists('/new_name.txt'))

        # Перемещение несуществующего файла
        output = self.capture_output(mv_cmd.execute, ['/nonexistent.txt', '/dest.txt'])
        self.assertIn('cannot stat', output)

    def test_zip_command(self):
        '''Тест zip'''
        zip_cmd = ZipCommand(self.logger)

        # Создание архива
        output = self.capture_output(zip_cmd.execute, ['/test', '/archive.zip'])
        self.assertIn('Created zip archive', output)
        self.assertTrue(os.path.exists('/archive.zip'))

    def test_unzip_command(self):
        '''тест unzip'''
        unzip_cmd = UnzipCommand(self.logger)

        # Распаковка несуществующего архива
        output = self.capture_output(unzip_cmd.execute, ['/nonexistent.zip'])
        self.assertIn('cannot open', output)

    def test_tar_command(self):
        '''тест tar'''
        tar_cmd = TarCommand(self.logger)

        # Создание tar архива
        output = self.capture_output(tar_cmd.execute, ['/test', '/backup.tar.gz'])
        self.assertIn('Created tar archive', output)

    def test_untar_command(self):
        '''тест untar'''
        untar_cmd = UntarCommand(self.logger)

        output = self.capture_output(untar_cmd.execute, ['/nonexistent.tar.gz'])
        self.assertIn('cannot open', output)

    def test_grep_command(self):
        '''тест grep'''
        grep_cmd = GrepCommand(self.logger)

        # Поиск в существующем файле с найденным шаблоном
        output = self.capture_output(grep_cmd.execute, ['World', '/test/file1.txt'])
        self.assertEqual(output.strip(), 'test\\file1.txt:1:Hello World!')

        # Поиск в существующем файле без найденного шаблона
        output = self.capture_output(grep_cmd.execute, ['NotFound', '/test/file1.txt'])
        self.assertEqual(output.strip(), 'No matches found')

        # Поиск в несуществующем файле
        output = self.capture_output(grep_cmd.execute, ['pattern', '/nonexistent.txt'])
        self.assertIn('No such file', output)

        # Поиск в директории вместо файла
        output = self.capture_output(grep_cmd.execute, ['pattern', '/test/subdir'])
        self.assertIn('Is a directory', output)

        # Поиск без указания файла
        output = self.capture_output(grep_cmd.execute, ['pattern'])
        self.assertIn('grep: missing operands\nUsage: grep [-r] [-i] <pattern> <path>\n', output)

        # Поиск без указания шаблона
        output = self.capture_output(grep_cmd.execute, [])
        self.assertIn('grep: missing operands\nUsage: grep [-r] [-i] <pattern> <path>\n', output)

        # Рекурсивный поиск в директории
        output = self.capture_output(grep_cmd.execute, ['-r', 'content', '/test'])
        self.assertIn(output.strip(), 'test\\file2.txt:1:Test content')

        # Поиск с игнорированием регистра
        output = self.capture_output(grep_cmd.execute, ['-i', 'hello', '/test/file1.txt'])
        self.assertEqual(output.strip(), 'test\\file1.txt:1:Hello World!')

    def test_cat_command_errors(self):
        # cat без аргументов
        cat_cmd = CATCommand(self.logger)
        output = self.capture_output(cat_cmd.execute, [])
        self.assertIn('missing file operand', output)

    def test_cp_command_errors(self):
        # cp без аргументов
        cp_cmd = CPCommand(self.logger)
        output = self.capture_output(cp_cmd.execute, [])
        self.assertIn('missing file operands', output)

    def test_rm_command_errors(self):
        # rm без аргументов
        rm_cmd = RMCommand(self.logger)
        output = self.capture_output(rm_cmd.execute, [])
        self.assertIn('missing operand', output)

