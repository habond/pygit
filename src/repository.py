"""
Repository management and operations.

Handles repository initialization, HEAD management, and branch operations.
"""

from pathlib import Path
from typing import Dict, Optional

from .objects import read_object, parse_tree_object

# Type alias for tree filename -> sha1 mappings
TreeMapping = Dict[str, str]


def init_repository(path: str = ".") -> None:
    """Initialize a new pygit repository"""
    repo_path = Path(path)
    pygit_dir = repo_path / ".pygit"

    if pygit_dir.exists():
        print(f"pygit repository already exists in {repo_path.absolute()}")
        return

    # Create .pygit directory structure
    pygit_dir.mkdir()
    (pygit_dir / "objects").mkdir()
    (pygit_dir / "refs").mkdir()
    (pygit_dir / "refs" / "heads").mkdir()

    # Create HEAD file pointing to main branch
    with open(pygit_dir / "HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")

    print(f"Initialized empty pygit repository in {pygit_dir.absolute()}")


def get_current_commit() -> Optional[str]:
    """Get the current commit SHA from HEAD"""
    head_path = Path(".pygit/HEAD")
    if not head_path.exists():
        return None

    with open(head_path) as f:
        head_content = f.read().strip()

    if head_content.startswith("ref: "):
        # HEAD points to a branch
        branch_ref = head_content[5:]  # Remove "ref: "
        branch_path = Path(f".pygit/{branch_ref}")
        if branch_path.exists():
            with open(branch_path) as f:
                return f.read().strip()
    else:
        # HEAD contains a commit SHA directly
        return head_content

    return None


def update_branch(commit_sha1: str) -> None:
    """Update the current branch to point to the new commit"""
    head_path = Path(".pygit/HEAD")
    with open(head_path) as f:
        head_content = f.read().strip()

    if head_content.startswith("ref: "):
        # HEAD points to a branch
        branch_ref = head_content[5:]  # Remove "ref: "
        branch_path = Path(f".pygit/{branch_ref}")
        branch_path.parent.mkdir(parents=True, exist_ok=True)

        with open(branch_path, "w") as f:
            f.write(commit_sha1 + "\n")
    else:
        # Update HEAD directly
        with open(head_path, "w") as f:
            f.write(commit_sha1 + "\n")


def get_current_tree_entries() -> TreeMapping:
    """Get entries from the current commit's tree"""
    current_commit = get_current_commit()
    if not current_commit:
        return {}

    try:
        # Get the commit object
        commit_obj = read_object(current_commit)
        if commit_obj["type"] != "commit":
            return {}

        # Parse commit to get tree SHA
        lines = commit_obj["content"].decode().split("\n")
        tree_sha = None
        for line in lines:
            if line.startswith("tree "):
                tree_sha = line.split()[1]
                break

        if not tree_sha:
            return {}

        # Get tree entries
        tree_obj = read_object(tree_sha)
        if tree_obj["type"] != "tree":
            return {}

        entries = parse_tree_object(tree_obj["content"])
        result = {}
        for entry in entries:
            result[entry["name"]] = entry["sha1"]

        return result
    except Exception:
        return {}
