"""
Index (staging area) management.

Handles the staging area where files are prepared for commit.
"""

from pathlib import Path
from typing import Dict

from .objects import hash_object, create_tree_object


def read_index() -> Dict[str, str]:
    """Read the index file (staging area)"""
    index_path = Path(".pygit/index")

    if not index_path.exists():
        return {}

    index = {}
    with open(index_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    sha1, filepath = parts
                    index[filepath] = sha1

    return index


def write_index(index: Dict[str, str]) -> None:
    """Write the index file (staging area)"""
    index_path = Path(".pygit/index")

    with open(index_path, "w") as f:
        for filepath in sorted(index.keys()):
            f.write(f"{index[filepath]}\t{filepath}\n")


def add_to_index(filepath: str) -> None:
    """Add a file to the staging area or stage its deletion"""
    index = read_index()

    if not Path(filepath).exists():
        # Check if file was previously tracked (in index or in current commit)
        from .repository import get_current_tree_entries

        current_tree_entries = get_current_tree_entries()
        filename = Path(filepath).name

        if filepath in index or filename in current_tree_entries:
            # File was tracked but now deleted - stage deletion with special marker
            index[filepath] = "DELETED"
            write_index(index)
            print(f"Staged deletion of '{filepath}'")
            return
        else:
            print(f"Error: file '{filepath}' not found")
            return

    # Hash the file as a blob and store it
    with open(filepath, "rb") as f:
        content = f.read()

    sha1 = hash_object(content, "blob", write=True)

    # Update index
    index[filepath] = sha1
    write_index(index)

    print(f"Added '{filepath}' to staging area")


def create_tree_from_index(current_tree_entries: Dict[str, str]) -> str:
    """Create a tree object from the current index, merged with current tree"""
    index = read_index()

    # Start with current tree entries (all previously committed files)
    merged_entries = current_tree_entries.copy()

    # Update with staged changes (skip deleted files)
    for filepath, sha1 in index.items():
        filename = Path(filepath).name
        if sha1 == "DELETED":
            # File is staged for deletion, remove it from merged_entries
            merged_entries.pop(filename, None)
        else:
            merged_entries[filename] = sha1

    if not merged_entries:
        return hash_object(b"", "tree", write=True)

    entries = []
    for filename, sha1 in merged_entries.items():
        entries.append({"mode": "100644", "name": filename, "sha1": sha1})

    return create_tree_object(entries)
