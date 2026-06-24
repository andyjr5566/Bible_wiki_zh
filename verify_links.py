import re
import os
import json

def verify_links(book_name=None, root_path=r'C:\Obsidian\Hermes\scripture'):
    # 1. Get all existing entity files
    existing_entities = set()
    for folder in ['人物', '地點', '主題']:
        folder_path = os.path.join(root_path, folder)
        if os.path.exists(folder_path):
            for f in os.listdir(folder_path):
                if f.endswith('.md'):
                    existing_entities.add(f[:-3])

    # 2. Scan for wikilinks
    # If book_name is None, scan all directories under root_path except the shared folders
    books_to_scan = []
    if book_name:
        books_to_scan = [book_name]
    else:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path) and item not in ['人物', '地點', '主題']:
                books_to_scan.append(item)

    all_broken = {}
    
    for book in books_to_scan:
        book_path = os.path.join(root_path, book)
        # Scan each section
        for section in ['經文', '註解', '拾穗', '解說', '背景', '綱要', '交叉參照']:
            section_path = os.path.join(book_path, section)
            if not os.path.exists(section_path):
                continue
            
            for fname in os.listdir(section_path):
                if not fname.endswith('.md'):
                    continue
                
                file_path = os.path.join(section_path, fname)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Skip binary files if any
                    continue
                
                # Find all [[links]]
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in links:
                    # Clean link (handle [[Name|Alias]] case)
                    entity = link.split('|')[0]
                    if entity not in existing_entities:
                        # Log the broken link
                        key = f"{book}/{section}/{fname}"
                        all_broken.setdefault(key, set()).add(entity)

    # 3. Process and output results
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
    
    # Save to JSON report
    report_path = os.path.join(root_path, 'broken_links_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    # Save to human readable text
    txt_path = os.path.join(root_path, 'missing_entities.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Broken Links Report - Total Unique: {len(all_unique_broken)}\n")
        f.write("="*50 + "\n")
        for entity in sorted(list(all_unique_broken)):
            f.write(f"[[{entity}]]\n")
            
    return report

if __name__ == "__main__":
    import sys
    target_book = sys.argv[1] if len(sys.argv) > 1 else None
    res = verify_links(target_book)
    print(f"Scan complete. Unique broken links found: {res['total_broken_unique']}")
    print(f"Report saved to broken_links_report.json and missing_entities.txt")