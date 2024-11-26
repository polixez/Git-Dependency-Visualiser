import unittest
import os
import tempfile
import subprocess
import shutil
import stat
from visualize_deps import get_commits, get_commit_data, build_graph, generate_graphviz_code

class TestVisualizeDeps(unittest.TestCase):

    def setUp(self):
        # Создаем временный Git-репозиторий для тестов
        self.repo_dir = tempfile.mkdtemp()
        subprocess.check_call(['git', '-C', self.repo_dir, 'init'])

        # Отключаем кеширование файловой системы Git на Windows
        subprocess.check_call(['git', '-C', self.repo_dir, 'config', 'core.fscache', 'false'])

        # Создаем тестовый файл и делаем коммиты
        self.file_name = 'test_file.txt'
        file_path = os.path.join(self.repo_dir, self.file_name)

        # Первый коммит с латиницей
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('First change')
        subprocess.check_call(['git', '-C', self.repo_dir, 'add', self.file_name])
        subprocess.check_call(['git', '-C', self.repo_dir, 'commit', '-m', 'Added test_file.txt'])

        # Второй коммит с кириллицей
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('Второе изменение')
        subprocess.check_call(['git', '-C', self.repo_dir, 'add', self.file_name])
        subprocess.check_call(['git', '-C', self.repo_dir, 'commit', '-m', 'Изменен test_file.txt'])

        # Получаем хэши коммитов для тестов
        self.commits = get_commits(self.repo_dir, self.file_name)

    def remove_readonly(self, func, path, exc_info):
        """
        Обработчик ошибок для удаления readonly файлов на Windows.
        """
        # Сбрасываем атрибут "только чтение"
        os.chmod(path, stat.S_IWRITE)
        # Повторяем попытку удаления
        func(path)

    def tearDown(self):
        # Удаляем временный репозиторий с обработчиком ошибок
        shutil.rmtree(self.repo_dir, onerror=self.remove_readonly)

    def test_get_commits(self):
        commits = get_commits(self.repo_dir, self.file_name)
        self.assertEqual(len(commits), 2)

    def test_get_commit_data(self):
        for commit_hash in self.commits:
            message, parents = get_commit_data(self.repo_dir, commit_hash)
            self.assertTrue(len(message) > 0)
            self.assertIsInstance(parents, list)

    def test_build_graph(self):
        graph = build_graph(self.repo_dir, self.commits)
        self.assertGreaterEqual(len(graph), 2)
        for commit_hash, data in graph.items():
            self.assertIn('message', data)
            self.assertIn('parents', data)

    def test_generate_graphviz_code(self):
        graph = build_graph(self.repo_dir, self.commits)
        graphviz_code = generate_graphviz_code(graph)
        self.assertIsInstance(graphviz_code, str)
        self.assertIn('digraph G {', graphviz_code)
        # Проверяем наличие сообщений коммитов
        self.assertIn('Added test_file.txt', graphviz_code)
        self.assertIn('Изменен test_file.txt', graphviz_code)

    def test_output_file(self):
        # Тестируем запись в файл
        graph = build_graph(self.repo_dir, self.commits)
        graphviz_code = generate_graphviz_code(graph)
        output_path = os.path.join(tempfile.gettempdir(), 'graph.dot')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(graphviz_code)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('digraph G {', content)
            # Проверяем наличие сообщений коммитов
            self.assertIn('Added test_file.txt', content)
            self.assertIn('Изменен test_file.txt', content)
        # Удаляем файл после теста
        os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
