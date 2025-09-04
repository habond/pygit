"""
Tests for the index module.
"""

from pathlib import Path

from src.index import (
    read_index,
    write_index,
    add_to_index,
    create_tree_from_index,
)
from src.objects import hash_object, read_object


def test_read_index_no_file(initialized_repo: Path) -> None:
    """Test reading index when no index file exists."""
    result = read_index()
    assert result == {}


def test_write_and_read_index(initialized_repo: Path) -> None:
    """Test writing and reading index."""
    test_index = {
        "file1.txt": "abc123",
        "file2.txt": "def456",
    }
    
    write_index(test_index)
    
    # Should create index file
    index_file = Path(".pygit/index")
    assert index_file.exists()
    
    # Should be able to read it back
    result = read_index()
    assert result == test_index


def test_add_to_index_file_not_found(initialized_repo: Path, capsys) -> None:
    """Test adding non-existent file to index."""
    add_to_index("nonexistent.txt")
    
    captured = capsys.readouterr()
    assert "not found" in captured.out
    
    # Index should remain empty
    assert read_index() == {}


def test_add_to_index_success(initialized_repo: Path, sample_file: Path) -> None:
    """Test successfully adding file to index."""
    add_to_index(str(sample_file))
    
    # Should update index
    index = read_index()
    assert str(sample_file) in index
    
    # Should store the blob
    blob_sha = index[str(sample_file)]
    obj_type, size, content = read_object(blob_sha)
    assert obj_type == "blob"
    assert content == sample_file.read_bytes()


def test_create_tree_from_index_empty(initialized_repo: Path) -> None:
    """Test creating tree from empty index."""
    tree_sha = create_tree_from_index({})
    
    # Should create empty tree
    obj_type, size, content = read_object(tree_sha)
    assert obj_type == "tree"
    assert content == b""


def test_create_tree_from_index_with_files(
    initialized_repo: Path, multiple_files: list[Path]
) -> None:
    """Test creating tree from index with files."""
    # Add files to index
    for file_path in multiple_files:
        add_to_index(str(file_path))
    
    # Create tree from index
    current_tree_entries = {}  # No previous commit
    tree_sha = create_tree_from_index(current_tree_entries)
    
    # Should create valid tree
    obj_type, size, content = read_object(tree_sha)
    assert obj_type == "tree"
    assert size > 0


def test_create_tree_from_index_merges_with_current(initialized_repo: Path) -> None:
    """Test that create_tree_from_index merges with existing tree entries."""
    # Simulate existing tree entries
    existing_blob_sha = hash_object(b"existing content", "blob", write=True)
    current_tree_entries = {
        "existing.txt": existing_blob_sha
    }
    
    # Add new file to index
    new_file = Path("new.txt")
    new_file.write_text("new content")
    add_to_index("new.txt")
    
    # Create tree - should include both existing and new files
    tree_sha = create_tree_from_index(current_tree_entries)
    
    # Verify tree was created
    obj_type, size, content = read_object(tree_sha)
    assert obj_type == "tree"
    assert size > 0


def test_write_index_sorts_entries(initialized_repo: Path) -> None:
    """Test that write_index sorts entries by filename."""
    test_index = {
        "zzz.txt": "hash3",
        "aaa.txt": "hash1", 
        "mmm.txt": "hash2",
    }
    
    write_index(test_index)
    
    # Read the raw index file
    index_content = Path(".pygit/index").read_text()
    lines = index_content.strip().split('\n')
    
    # Should be sorted alphabetically
    assert lines[0].endswith("aaa.txt")
    assert lines[1].endswith("mmm.txt")  
    assert lines[2].endswith("zzz.txt")