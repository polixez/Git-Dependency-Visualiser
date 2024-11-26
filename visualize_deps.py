import argparse
import subprocess
import sys
from collections import deque

def get_commits(repo_path, file_name):
    cmd = ['git', '-C', repo_path, 'log', '--pretty=%H', '--encoding=UTF-8', '--', file_name]
    result = subprocess.check_output(cmd, encoding='utf-8', errors='replace')
    commits = result.strip().split('\n')
    return commits

def get_commit_data(repo_path, commit_hash):
    cmd_message = ['git', '-C', repo_path, 'log', '-1', '--pretty=%B', '--encoding=UTF-8', commit_hash]
    cmd_parents = ['git', '-C', repo_path, 'log', '-1', '--pretty=%P', '--encoding=UTF-8', commit_hash]
    message = subprocess.check_output(cmd_message, encoding='utf-8', errors='replace').strip()
    parents = subprocess.check_output(cmd_parents, encoding='utf-8', errors='replace').strip().split()
    return message, parents

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

if __name__ == '__main__':
    main()
