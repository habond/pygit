"""
Command-line interface for pygit.

Handles argument parsing and dispatches to appropriate command functions.
"""

import sys

from .commands import (
    add_command,
    cat_file_command,
    commit_command,
    commit_tree_command,
    hash_object_command,
    ls_tree_command,
    status_command,
    write_tree_command,
)
from .repository import init_repository


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("Commands:")
        print("  init [path] - Initialize a new pygit repository")
        print("  hash-object [-w] <file> - Hash a file and optionally store it")
        print("  cat-file [-t|-s] <sha1> - Display object contents, type, or size")
        print("  write-tree - Create a tree object from current directory")
        print("  ls-tree <sha1> - List the contents of a tree object")
        print(
            "  commit-tree <tree-sha1> [-m <message>] [-p <parent>] - "
            "Create a commit object"
        )
        print("  add <file> - Add a file to the staging area")
        print("  status - Show working tree status")
        print("  commit [-m <message>] - Create a commit from staged files")
        return

    command = sys.argv[1]

    if command == "init":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        init_repository(path)
    elif command == "hash-object":
        if len(sys.argv) < 3:
            print("Usage: python main.py hash-object [-w] <file>")
            return

        write = False
        file_path = None

        for arg in sys.argv[2:]:
            if arg == "-w":
                write = True
            else:
                file_path = arg

        if not file_path:
            print("Error: file path required")
            return

        hash_object_command(file_path, write)
    elif command == "cat-file":
        if len(sys.argv) < 3:
            print("Usage: python main.py cat-file [-t|-s] <sha1>")
            return

        show_type = False
        show_size = False
        sha1 = None

        for arg in sys.argv[2:]:
            if arg == "-t":
                show_type = True
            elif arg == "-s":
                show_size = True
            else:
                sha1 = arg

        if not sha1:
            print("Error: SHA-1 hash required")
            return

        cat_file_command(sha1, show_type, show_size)
    elif command == "write-tree":
        tree_sha1 = write_tree_command()
        print(tree_sha1)
    elif command == "ls-tree":
        if len(sys.argv) < 3:
            print("Usage: python main.py ls-tree <sha1>")
            return
        sha1 = sys.argv[2]
        ls_tree_command(sha1)
    elif command == "commit-tree":
        if len(sys.argv) < 3:
            print(
                "Usage: python main.py commit-tree <tree-sha1> "
                "[-m <message>] [-p <parent>]"
            )
            return

        tree_sha1 = sys.argv[2]
        message = ""
        parent = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "-m" and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "-p" and i + 1 < len(sys.argv):
                parent = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        commit_sha1 = commit_tree_command(tree_sha1, message, parent)
        print(commit_sha1)
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: python main.py add <file>")
            return
        filepath = sys.argv[2]
        add_command(filepath)
    elif command == "status":
        status_command()
    elif command == "commit":
        message = ""

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "-m" and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        if not message:
            message = input("Commit message: ")

        commit_command(message)
    else:
        print(f"Unknown command: {command}")
