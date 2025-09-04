"""
High-level command implementations.

Contains the business logic for each pygit command.
"""

from pathlib import Path
from typing import Optional

from .index import add_to_index, read_index, write_index, create_tree_from_index
from .objects import (
    hash_object,
    read_object,
    create_tree_object,
    parse_tree_object,
    create_commit_object,
)
from .repository import get_current_commit, update_branch, get_current_tree_entries


def hash_object_command(file_path: str, write: bool = False) -> None:
    """Hash a file and optionally store it as a blob object"""
    if not Path(file_path).exists():
        print(f"Error: file '{file_path}' not found")
        return

    with open(file_path, "rb") as f:
        content = f.read()

    sha1 = hash_object(content, "blob", write)
    print(sha1)


def cat_file_command(
    sha1: str, show_type: bool = False, show_size: bool = False
) -> None:
    """Display the contents of a git object"""
    try:
        obj_type, size, content = read_object(sha1)

        if show_type:
            print(obj_type)
        elif show_size:
            print(size)
        else:
            print(content.decode(), end="")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error reading object: {e}")


def write_tree_command(directory: str = ".") -> str:
    """Create a tree object from current directory"""
    entries = []

    for item in sorted(Path(directory).iterdir()):
        if item.name.startswith("."):
            continue

        if item.is_file():
            # Hash the file as a blob
            with open(item, "rb") as f:
                content = f.read()
            sha1 = hash_object(content, "blob", write=True)
            entries.append(
                {"mode": "100644", "name": item.name, "sha1": sha1}  # regular file
            )
        elif item.is_dir():
            # Recursively create tree for subdirectory
            subtree_sha1 = write_tree_command(str(item))
            entries.append(
                {"mode": "40000", "name": item.name, "sha1": subtree_sha1}  # directory
            )

    if entries:
        return create_tree_object(entries)
    else:
        # Empty tree
        return hash_object(b"", "tree", write=True)


def ls_tree_command(sha1: str) -> None:
    """List the contents of a tree object"""
    try:
        obj_type, size, content = read_object(sha1)

        if obj_type != "tree":
            print(f"Error: {sha1} is not a tree object")
            return

        entries = parse_tree_object(content)
        for entry in entries:
            mode = entry["mode"]
            obj_sha1 = entry["sha1"]
            name = entry["name"]

            # Determine type from mode
            if mode == "40000":
                obj_type = "tree"
            else:
                obj_type = "blob"

            print(f"{mode} {obj_type} {obj_sha1}\t{name}")

    except Exception as e:
        print(f"Error: {e}")


def commit_tree_command(
    tree_sha1: str, message: str = "", parent: Optional[str] = None
) -> str:
    """Create a commit object"""
    return create_commit_object(tree_sha1, parent, message)


def add_command(filepath: str) -> None:
    """Add a file to the staging area"""
    add_to_index(filepath)


def status_command() -> None:
    """Show the status of the working tree and staging area"""
    index = read_index()

    print("Staged files:")
    if index:
        for filepath in sorted(index.keys()):
            print(f"  {filepath}")
    else:
        print("  (no files staged)")

    print("\nUntracked files:")
    tracked_files = set(index.keys())
    untracked_found = False

    for item in Path(".").iterdir():
        if item.name.startswith("."):
            continue
        if item.is_file() and str(item) not in tracked_files:
            print(f"  {item}")
            untracked_found = True

    if not untracked_found:
        print("  (none)")


def commit_command(message: str = "") -> None:
    """Create a commit from staged files"""
    index = read_index()
    if not index:
        print("Error: no files staged for commit")
        return

    # Create tree from staging area
    current_tree_entries = get_current_tree_entries()
    tree_sha1 = create_tree_from_index(current_tree_entries)

    # Get current commit for parent
    parent_sha1 = get_current_commit()

    # Create commit
    commit_sha1 = create_commit_object(tree_sha1, parent_sha1, message)

    # Update current branch
    update_branch(commit_sha1)

    # Clear the index after successful commit
    write_index({})

    print(f"Created commit {commit_sha1}")
    if parent_sha1:
        print(f"Parent: {parent_sha1}")


def checkout_command(commit_sha1: str) -> None:
    """Checkout files from a specific commit"""
    try:
        # Get the commit object
        obj_type, size, content = read_object(commit_sha1)
        if obj_type != "commit":
            print(f"Error: {commit_sha1} is not a commit object")
            return

        # Parse commit to get tree SHA
        lines = content.decode().split("\n")
        tree_sha = None
        for line in lines:
            if line.startswith("tree "):
                tree_sha = line.split()[1]
                break

        if not tree_sha:
            print("Error: commit has no tree")
            return

        # Get tree entries
        obj_type, size, tree_content = read_object(tree_sha)
        if obj_type != "tree":
            print("Error: invalid tree object")
            return

        entries = parse_tree_object(tree_content)

        # Clear working directory (except .pygit)
        for item in Path(".").iterdir():
            if item.name.startswith("."):
                continue
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil

                shutil.rmtree(item)

        # Restore files from the tree
        for entry in entries:
            if entry["mode"] == "40000":  # Directory
                # For now, skip directories - this is a basic implementation
                continue
            else:  # Regular file
                # Get the blob content
                blob_type, blob_size, blob_content = read_object(entry["sha1"])
                if blob_type == "blob":
                    with open(entry["name"], "wb") as f:
                        f.write(blob_content)

        print(f"Checked out commit {commit_sha1}")

    except FileNotFoundError:
        print(f"Error: commit {commit_sha1} not found")
    except Exception as e:
        print(f"Error during checkout: {e}")


def log_command() -> None:
    """Show commit history starting from HEAD"""
    try:
        # Start from the current commit
        current_commit = get_current_commit()
        if not current_commit:
            print("No commits found")
            return

        commit_sha: Optional[str] = current_commit
        while commit_sha:
            # Get the commit object
            obj_type, size, content = read_object(commit_sha)
            if obj_type != "commit":
                print(f"Error: {commit_sha} is not a commit object")
                break

            # Parse commit content
            lines = content.decode().split("\n")
            parent_sha = None
            author = "Unknown"
            message = ""

            # Parse commit headers and message
            in_message = False
            for line in lines:
                if not in_message:
                    if line.startswith("tree "):
                        pass  # We don't need the tree SHA for log display
                    elif line.startswith("parent "):
                        parent_sha = line.split()[1]
                    elif line.startswith("author "):
                        # Format: author Name <email> timestamp timezone
                        author_parts = line.split(" ", 1)
                        if len(author_parts) > 1:
                            author = author_parts[1]
                    elif line == "":
                        in_message = True
                else:
                    if line.strip():  # Skip empty lines in message
                        if message:
                            message += " " + line.strip()
                        else:
                            message = line.strip()

            # Display commit info in git log format
            print(f"commit {commit_sha}")
            print(f"Author: {author}")
            print()
            print(f"    {message}")
            print()

            # Move to parent commit
            commit_sha = parent_sha

    except FileNotFoundError:
        print("Error: repository not initialized or corrupted")
    except Exception as e:
        print(f"Error reading commit history: {e}")
