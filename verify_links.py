import re
import os
import json

def verify_links(book_name=None, root_path=r'C:\Obsidian\Hermes\scripture'):
    """
    Verify all wiki-links in scripture project.
    
    New architecture (v2):
    - Chapter files: 【書名】/第x章.md  (not 【書名】/經文/第x章.md)
    - Link folders: link_folder/人物/, link_folder/地點/, link_folder/主題/, etc.
    
    Old architecture files (經文/, 註解/, etc.) still supported for backward compat.
    """

    # 1. Build entity registry from ALL link folders (now under link_folder/)
    link_folder_parent = 'link_folder'
    link_folders = [
        '人物', '地點', '主題', '背景', '歷史', '原文',
        '文化', '神學', '互文', '解經爭議',
    ]
    
    existing_entities = set()  # just the entity name
    entity_locations = {}     # entity_name → folder/filename
    
    for folder in link_folders:
        folder_path = os.path.join(root_path, link_folder_parent, folder)
        if not os.path.exists(folder_path):
            continue
        for f in os.listdir(folder_path):
            if f.endswith('.md'):
                entity_name = f[:-3]
                existing_entities.add(entity_name)
                entity_locations[entity_name] = os.path.join(link_folder_parent, folder, f)

    # 2. Build set of valid chapter-level wikilinks
    existing_chapter_links = set()
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if not os.path.isdir(item_path):
            continue
        if item in [link_folder_parent] + link_folders:
            continue
        
        # New architecture: 【書名】/第x章.md
        for fname in os.listdir(item_path):
            if fname.startswith('第') and fname.endswith('.md'):
                chapter = fname.replace('.md', '')
                existing_chapter_links.add(f"{item} {chapter}")
                existing_chapter_links.add(f"{item}/{chapter}")
        
        # Old architecture: 【書名】/經文/第x章.md, etc.
        for section in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
            section_path = os.path.join(item_path, section)
            if not os.path.exists(section_path):
                continue
            for fname in os.listdir(section_path):
                if fname.endswith('.md'):
                    chapter = fname.replace('.md', '')
                    existing_chapter_links.add(f"{item} {chapter}")
                    existing_chapter_links.add(f"{item} {chapter} {section}")

    # 3. Scan for wiki-links
    books_to_scan = []
    if book_name:
        books_to_scan = [book_name]
    else:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path) and item not in [link_folder_parent] + link_folders:
                books_to_scan.append(item)

    all_broken = {}

    for book in books_to_scan:
        book_path = os.path.join(root_path, book)
        if not os.path.isdir(book_path):
            continue
        
        # Scan files in book folder (new architecture: 第x章.md directly)
        for item in os.listdir(book_path):
            if item.startswith('.'):
                continue
            file_path = os.path.join(book_path, item)
            
            if os.path.isfile(file_path) and item.endswith('.md'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    continue
                
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in links:
                    entity = link.split('|')[0]
                    entity_clean = entity.strip()
                    if entity_clean not in existing_entities and entity_clean not in existing_chapter_links:
                        key = f"{book}/{item}"
                        all_broken.setdefault(key, set()).add(entity_clean)
            
            elif os.path.isdir(file_path) and item in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
                for fname in os.listdir(file_path):
                    if not fname.endswith('.md'):
                        continue
                    filepath = os.path.join(file_path, fname)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        continue
                    
                    links = re.findall(r'\[\[([^\]]+)\]\]', content)
                    for link in links:
                        entity = link.split('|')[0]
                        entity_clean = entity.strip()
                        if entity_clean not in existing_entities and entity_clean not in existing_chapter_links:
                            key = f"{book}/{item}/{fname}"
                            all_broken.setdefault(key, set()).add(entity_clean)

    # Also scan all link folder files for outbound links
    for folder in link_folders:
        folder_path = os.path.join(root_path, link_folder_parent, folder)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if not fname.endswith('.md'):
                continue
            filepath = os.path.join(folder_path, fname)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
            
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                entity = link.split('|')[0]
                entity_clean = entity.strip()
                if entity_clean not in existing_entities and entity_clean not in existing_chapter_links:
                    key = f"{link_folder_parent}/{folder}/{fname}"
                    all_broken.setdefault(key, set()).add(entity_clean)

    # 4. Build report
    report = {
        "total_broken_unique": 0,
        "broken_links": [],
        "details": {}
    }
    
    all_unique_broken = set()
    for file, links in all_broken.items():
        all_unique_broken.update(links)
        report["details"][file] = sorted(list(links))
    
    report["total_broken_unique"] = len(all_unique_broken)
    report["broken_links"] = sorted(list(all_unique_broken))
    
    # 5. Save reports
    report_path = os.path.join(root_path, 'broken_links_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    txt_path = os.path.join(root_path, 'missing_entities.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Broken Links Report - Total Unique: {len(all_unique_broken)}\n")
        f.write("=" * 50 + "\n")
        for entity in sorted(list(all_unique_broken)):
            f.write(f"[[{entity}]]\n")
            
    return report

if __name__ == "__main__":
    import sys
    target_book = sys.argv[1] if len(sys.argv) > 1 else None
    res = verify_links(target_book)
    print(f"Scan complete. Unique broken links found: {res['total_broken_unique']}")
    print(f"Report saved to broken_links_report.json and missing_entities.txt")
