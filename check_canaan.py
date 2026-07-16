with open('c:/Obsidian/Hermes/scripture/link_folder/人物/迦南人.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
markers = re.findall(r'<!-- accumulation:([^:]+):(\d+):start -->', content)
for book, chapter in markers:
    print(f'Book: "{book}" Chapter: {chapter}')