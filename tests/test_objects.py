"""
Tests for the objects module.
"""

import pytest
from pathlib import Path

from src.objects import (
    hash_object,
    read_object,
    create_tree_object,
    parse_tree_object,
    create_commit_object,
)


def test_hash_object_without_write(temp_repo: Path) -> None:
    """Test hashing data without writing to storage."""
    data = b"Hello, World!"
    sha1 = hash_object(data, "blob", write=False)
    
    # Should return a SHA-1 hash
    assert len(sha1) == 40
    assert all(c in "0123456789abcdef" for c in sha1)
    
    # Should be consistent
    assert hash_object(data, "blob", write=False) == sha1
    
    # Should not create any files
    assert not (Path(".pygit/objects") / sha1[:2]).exists()


def test_hash_object_with_write(initialized_repo: Path) -> None:
    """Test hashing data and writing to storage."""
    data = b"Hello, World!"
    sha1 = hash_object(data, "blob", write=True)
    
    # Should create the object file
    obj_path = Path(".pygit/objects") / sha1[:2] / sha1[2:]
    assert obj_path.exists()
    
    # Should be able to read it back
    obj_type, size, content = read_object(sha1)
    assert obj_type == "blob"
    assert size == len(data)
    assert content == data


def test_read_object_not_found(initialized_repo: Path) -> None:
    """Test reading a non-existent object."""
    fake_sha1 = "a" * 40
    
    with pytest.raises(FileNotFoundError, match="Object .* not found"):
        read_object(fake_sha1)


def test_create_tree_object(initialized_repo: Path) -> None:
    """Test creating a tree object."""
    # First create some blobs
    blob1_sha = hash_object(b"file1 content", "blob", write=True)
    blob2_sha = hash_object(b"file2 content", "blob", write=True)
    
    entries = [
        {"mode": "100644", "name": "file1.txt", "sha1": blob1_sha},
        {"mode": "100644", "name": "file2.txt", "sha1": blob2_sha},
    ]
    
    tree_sha = create_tree_object(entries)
    
    # Should return a valid SHA-1
    assert len(tree_sha) == 40
    
    # Should be able to read the tree back
    obj_type, size, content = read_object(tree_sha)
    assert obj_type == "tree"
    assert size > 0


def test_parse_tree_object(initialized_repo: Path) -> None:
    """Test parsing tree object content."""
    # Create a tree first
    blob1_sha = hash_object(b"file1 content", "blob", write=True)
    blob2_sha = hash_object(b"file2 content", "blob", write=True)
    
    original_entries = [
        {"mode": "100644", "name": "file1.txt", "sha1": blob1_sha},
        {"mode": "100644", "name": "file2.txt", "sha1": blob2_sha},
    ]
    
    tree_sha = create_tree_object(original_entries)
    
    # Read and parse the tree
    obj_type, size, content = read_object(tree_sha)
    parsed_entries = parse_tree_object(content)
    
    # Should match original entries (sorted by name)
    expected_entries = sorted(original_entries, key=lambda x: x["name"])
    assert parsed_entries == expected_entries


def test_create_commit_object(initialized_repo: Path) -> None:
    """Test creating a commit object."""
    # Create a tree first
    blob_sha = hash_object(b"file content", "blob", write=True)
    entries = [{"mode": "100644", "name": "file.txt", "sha1": blob_sha}]
    tree_sha = create_tree_object(entries)
    
    # Create commit
    commit_sha = create_commit_object(
        tree_sha,
        parent_sha1=None,
        message="Initial commit",
        author="Test User <test@example.com>"
    )
    
    # Should return a valid SHA-1
    assert len(commit_sha) == 40
    
    # Should be able to read the commit back
    obj_type, size, content = read_object(commit_sha)
    assert obj_type == "commit"
    
    commit_text = content.decode()
    assert f"tree {tree_sha}" in commit_text
    assert "Initial commit" in commit_text
    assert "Test User <test@example.com>" in commit_text


def test_create_commit_object_with_parent(initialized_repo: Path) -> None:
    """Test creating a commit object with a parent."""
    # Create tree and first commit
    blob_sha = hash_object(b"file content", "blob", write=True)
    entries = [{"mode": "100644", "name": "file.txt", "sha1": blob_sha}]
    tree_sha = create_tree_object(entries)
    
    parent_sha = create_commit_object(tree_sha, message="First commit")
    
    # Create child commit
    child_sha = create_commit_object(
        tree_sha,
        parent_sha1=parent_sha,
        message="Second commit"
    )
    
    # Child commit should reference parent
    obj_type, size, content = read_object(child_sha)
    commit_text = content.decode()
    assert f"parent {parent_sha}" in commit_text
    assert "Second commit" in commit_text


def test_different_object_types_have_different_hashes(temp_repo: Path) -> None:
    """Test that the same content with different types produces different hashes."""
    data = b"same content"
    
    blob_hash = hash_object(data, "blob", write=False)
    tree_hash = hash_object(data, "tree", write=False)
    commit_hash = hash_object(data, "commit", write=False)
    
    # All should be different because the type is part of the hash
    assert blob_hash != tree_hash
    assert blob_hash != commit_hash
    assert tree_hash != commit_hash