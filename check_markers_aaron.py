import re
content = open('c:/Obsidian/Hermes/scripture/link_folder/人物/亞倫.md', 'r', encoding='utf-8').read()
markers = re.findall(r'<!-- accumulation:([^:]+):(\d+):start -->', content)
for book, chapter in markers:
    print(f'Book: "{book}" Chapter: {chapter}')