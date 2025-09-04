"""
Git object storage and manipulation.

Handles blobs, trees, and commits - the core data structures of git.
"""

import hashlib
import zlib
from pathlib import Path
from typing import List, Optional, TypedDict, Literal, cast

# Git object types
GitObjectType = Literal["blob", "tree", "commit"]


class TreeEntry(TypedDict):
    """A single entry in a Git tree object."""

    mode: str  # File mode (e.g., "100644", "100755", "040000")
    name: str  # File or directory name
    sha1: str  # SHA-1 hash of the object


class GitObject(TypedDict):
    """A Git object with its type, size, and content."""

    type: GitObjectType  # Object type (blob, tree, commit)
    size: int  # Size of the content in bytes
    content: bytes  # Raw object content


def hash_object(
    data: bytes, obj_type: GitObjectType = "blob", write: bool = False
) -> str:
    """Create a git object hash from data"""
    # Git format: "<type> <size>\0<content>"
    header = f"{obj_type} {len(data)}".encode() + b"\0"
    store_data = header + data

    # Calculate SHA-1 hash
    sha1 = hashlib.sha1(store_data).hexdigest()

    if write:
        # Store in .pygit/objects/xx/xxxxx format
        obj_dir = Path(".pygit/objects") / sha1[:2]
        obj_dir.mkdir(exist_ok=True)

        obj_file = obj_dir / sha1[2:]
        with open(obj_file, "wb") as f:
            f.write(zlib.compress(store_data))

    return sha1


def read_object(sha1: str) -> GitObject:
    """Read and decompress an object from storage"""
    obj_file = Path(".pygit/objects") / sha1[:2] / sha1[2:]

    if not obj_file.exists():
        raise FileNotFoundError(f"Object {sha1} not found")

    with open(obj_file, "rb") as f:
        compressed_data = f.read()

    # Decompress and parse
    decompressed_data = zlib.decompress(compressed_data)

    # Split header and content
    null_index = decompressed_data.index(b"\0")
    header = decompressed_data[:null_index].decode()
    content = decompressed_data[null_index + 1 :]

    obj_type_str, size_str = header.split()
    obj_type = cast(GitObjectType, obj_type_str)  # Trust that stored objects are valid
    return GitObject(type=obj_type, size=int(size_str), content=content)


def create_tree_object(entries: List[TreeEntry]) -> str:
    """Create a tree object from a list of entries"""
    # Tree format: <mode> <name>\0<20-byte-sha1>
    tree_data = b""

    # Sort entries by name (git requirement)
    sorted_entries = sorted(entries, key=lambda x: x["name"])

    for entry in sorted_entries:
        mode = entry["mode"].encode()
        name = entry["name"].encode()
        sha1_bytes = bytes.fromhex(entry["sha1"])

        tree_data += mode + b" " + name + b"\0" + sha1_bytes

    return hash_object(tree_data, "tree", write=True)


def parse_tree_object(content: bytes) -> List[TreeEntry]:
    """Parse tree object content into entries"""
    entries = []
    i = 0

    while i < len(content):
        # Find space after mode
        space_idx = content.index(b" ", i)
        mode = content[i:space_idx].decode()

        # Find null after name
        null_idx = content.index(b"\0", space_idx + 1)
        name = content[space_idx + 1 : null_idx].decode()

        # Get 20-byte SHA-1
        sha1_bytes = content[null_idx + 1 : null_idx + 21]
        sha1 = sha1_bytes.hex()

        entries.append(TreeEntry(mode=mode, name=name, sha1=sha1))

        i = null_idx + 21

    return entries


def create_commit_object(
    tree_sha1: str,
    parent_sha1: Optional[str] = None,
    message: str = "",
    author: str = "pygit user <user@example.com>",
) -> str:
    """Create a commit object"""
    import time

    timestamp = str(int(time.time()))
    timezone = "+0000"

    commit_data = f"tree {tree_sha1}\n"

    if parent_sha1:
        commit_data += f"parent {parent_sha1}\n"

    commit_data += f"author {author} {timestamp} {timezone}\n"
    commit_data += f"committer {author} {timestamp} {timezone}\n"
    commit_data += f"\n{message}\n"

    return hash_object(commit_data.encode(), "commit", write=True)
