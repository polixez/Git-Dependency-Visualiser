# Визуализатор зависимостей Git-репозитория

## Общее описание

Данный проект реализует инструмент командной строки для построения и визуализации графа зависимостей коммитов Git-репозитория, включая транзитивные зависимости. Инструмент используется для анализа истории изменений файла в репозитории с выводом графа зависимостей в формате Graphviz.

Граф включает сообщения коммитов и отображает связи между родительскими и дочерними коммитами. Это позволяет пользователю визуально представить историю изменений указанного файла.

---

## Функции и настройки

### Основные функции

- **Построение графа зависимостей:**
  - Визуализация коммитов и их связей в формате Graphviz.
- **Поддержка транзитивных зависимостей:**
  - Автоматический анализ всех родительских коммитов.
- **Гибкая настройка ввода и вывода:**
  - Указание пути к репозиторию, имени файла, сохранение результата в файл и опциональная генерация изображения графа.
- **Вывод на экран:**
  - Код Graphviz выводится в консоль.

### Параметры командной строки

- `--graphviz_path`: путь к программе Graphviz (`dot`) для генерации изображений.
- `--repo_path`: путь к анализируемому Git-репозиторию.
- `--output_path`: путь для сохранения результата в формате `.dot`.
- `--file_name`: имя файла, для которого строится граф зависимостей.

### Реализация функций
1. **Возвращение списка хэшей коммитов:**
    ```python
    def get_commits(repo_path, file_name):
    cmd = ['git', '-C', repo_path, 'log', '--pretty=%H', '--encoding=UTF-8', '--', file_name]
    result = subprocess.check_output(cmd, encoding='utf-8', errors='replace')
    commits = result.strip().split('\n')
    return commits
2. **Возвращение сообщения и родительских коммитов:**
    ```python
    get_commit_data(repo_path, commit_hash):
    cmd_message = ['git', '-C', repo_path, 'log', '-1', '--pretty=%B', '--encoding=UTF-8', commit_hash]
    cmd_parents = ['git', '-C', repo_path, 'log', '-1', '--pretty=%P', '--encoding=UTF-8', commit_hash]
    message = subprocess.check_output(cmd_message, encoding='utf-8', errors='replace').strip()
    parents = subprocess.check_output(cmd_parents, encoding='utf-8', errors='replace').strip().split()
    return message, parents
3. **Постройка графа зависимостей коммитов:**
    ```pythin
    def build_graph(repo_path, commits):
    graph = {}
    visited = set()
    queue = deque(commits)

    while queue:
        commit_hash = queue.popleft()
        if commit_hash in visited:
            continue
        visited.add(commit_hash)
        message, parents = get_commit_data(repo_path, commit_hash)
        graph[commit_hash] = {'message': message, 'parents': parents}
        queue.extend(parents)

    return graph
   
4. **Генерация текстового кода графа в формате Graphiz:**
    ```python
   def generate_graphviz_code(graph):
    lines = []
    lines.append('digraph G {')
    lines.append('    graph [charset="UTF-8"];')
    lines.append('    node [fontname="DejaVu Sans"];')
    lines.append('    edge [fontname="DejaVu Sans"];')
    for commit_hash, data in graph.items():
        label = f'{commit_hash[:7]}: {data["message"]}'
        # Экранируем специальные символы
        label = label.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'    "{commit_hash}" [label="{label}"];')
        for parent in data['parents']:
            lines.append(f'    "{parent}" -> "{commit_hash}";')
    lines.append('}')
    return '\n'.join(lines)
5. **Основная функция main:**
    ```python
    def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graphviz_path', help='Путь к Graphviz (dot).')
    parser.add_argument('--repo_path', required=True, help='Путь к Git-репозиторию.')
    parser.add_argument('--output_path', help='Путь для сохранения файла Graphviz.')
    parser.add_argument('--file_name', required=True, help='Имя файла для анализа.')
    args = parser.parse_args()

    commits = get_commits(args.repo_path, args.file_name)
    if not commits:
        print(f"Не найдено коммитов для файла {args.file_name}.")
        sys.exit(1)

    graph = build_graph(args.repo_path, commits)
    graphviz_code = generate_graphviz_code(graph)

    # Выводим код на экран
    print(graphviz_code)

    # Сохраняем код в файл, если указан путь
    if args.output_path:
        with open(args.output_path, 'w', encoding='utf-8') as f:
            f.write(graphviz_code)
        print(f"Graphviz файл сохранен в {args.output_path}")

    # Генерация изображения графа, если указан путь к Graphviz
    if args.graphviz_path and args.output_path:
        output_image = args.output_path.rsplit('.', 1)[0] + '.png'
        cmd = [args.graphviz_path, '-Tpng', args.output_path, '-o', output_image]
        subprocess.check_call(cmd)
        print(f"Изображение графа сохранено в {output_image}")
    elif args.graphviz_path and not args.output_path:
        print("Для генерации изображения необходимо указать путь к файлу результата (--output_path).")

### Стартовый скрипт
При запуске визуализатора можно указать стартовый скрипт, содержащий список команд для автоматического выполнения.

**Пример** ```build.bat```:
````
@echo off
echo Running tests...

python -m unittest discover -s tests.

echo Build completed.
````

---



## Команды для сборки проекта

1. **Установка зависимостей:**
   Проект не требует установки сторонних библиотек. Достаточно Python (>=3.7) и установленного Git.

2. **Запуск тестов:**
   Для проверки корректности функций выполните:
   ```bash
   python -m unittest discover -s tests
3. **Запуск визуализатора:**
   Для запуска проекта используйте:
   ```bash
   python visualize_deps.py --repo_path <путь_к_репозиторию> --file_name <имя_файла>

---
 
## Примеры использования

Запуск визуализатора:

    
    python visualize_deps.py --repo_path C:/<директория проекта>/test_repo --file_name test_file.txt

    
 **Пример сеанса работы:**

 С помощью ручного ввода рассмотрим как работает визуализатор
 


Используя наш тестовый репозиторий test_repo в данной сесии, в результате видим что визуализатор верно выполняет свою работу

---

## Результаты прогонов тестов

**Тестовый файл для проверки всех функций**
````
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

````
Запуск тестов с помощью ```build.bat```:
````
./build.bat
````

**Вывод**:

````
Running tests...
Initialized empty Git repository in C:/Users/korot/AppData/Local/Temp/tmpk671du3o/.git/
[master (root-commit) ae0462a] Added test_file.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
[master ee642d8] Изменен test_file.txt
 1 file changed, 1 insertion(+), 1 deletion(-)
.Initialized empty Git repository in C:/Users/korot/AppData/Local/Temp/tmphu1d35al/.git/
[master (root-commit) ae0462a] Added test_file.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
[master ee642d8] Изменен test_file.txt
 1 file changed, 1 insertion(+), 1 deletion(-)
.Initialized empty Git repository in C:/Users/korot/AppData/Local/Temp/tmp0nja5nbg/.git/
[master (root-commit) ae0462a] Added test_file.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
[master ee642d8] Изменен test_file.txt
 1 file changed, 1 insertion(+), 1 deletion(-)
.Initialized empty Git repository in C:/Users/korot/AppData/Local/Temp/tmpjm_fgqk1/.git/
[master (root-commit) b107d02] Added test_file.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
[master ae468a4] Изменен test_file.txt
 1 file changed, 1 insertion(+), 1 deletion(-)
.Initialized empty Git repository in C:/Users/korot/AppData/Local/Temp/tmp3at1d6b1/.git/
[master (root-commit) b107d02] Added test_file.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
[master ae468a4] Изменен test_file.txt
 1 file changed, 1 insertion(+), 1 deletion(-)
.
----------------------------------------------------------------------
Ran 5 tests in 1.628s

OK
Build completed.

````
Все тесты успешно пройдены, что подтверждает корректность работы всех функций визуализатора.

