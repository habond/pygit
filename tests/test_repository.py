"""
Tests for the repository module.
"""

from pathlib import Path
from pytest import CaptureFixture

from src.repository import (
    init_repository,
    get_current_commit,
    update_branch,
    get_current_tree_entries,
)
from src.objects import hash_object, create_tree_object, create_commit_object, TreeEntry


def test_init_repository(temp_repo: Path) -> None:
    """Test repository initialization."""
    init_repository()

    # Should create .pygit directory structure
    pygit_dir = Path(".pygit")
    assert pygit_dir.exists()
    assert pygit_dir.is_dir()

    # Should create subdirectories
    assert (pygit_dir / "objects").exists()
    assert (pygit_dir / "refs").exists()
    assert (pygit_dir / "refs" / "heads").exists()

    # Should create HEAD file
    head_file = pygit_dir / "HEAD"
    assert head_file.exists()
    assert head_file.read_text() == "ref: refs/heads/main\n"


def test_init_repository_already_exists(
    temp_repo: Path, capsys: CaptureFixture[str]
) -> None:
    """Test initializing repository when one already exists."""
    # Initialize once
    init_repository()

    # Initialize again
    init_repository()

    # Should print message about existing repository
    captured = capsys.readouterr()
    assert "already exists" in captured.out


def test_get_current_commit_no_repo(temp_repo: Path) -> None:
    """Test getting current commit when no repository exists."""
    result = get_current_commit()
    assert result is None


def test_get_current_commit_no_commits(initialized_repo: Path) -> None:
    """Test getting current commit when repository exists but no commits."""
    result = get_current_commit()
    assert result is None


def test_get_current_commit_with_commits(initialized_repo: Path) -> None:
    """Test getting current commit when commits exist."""
    # Create a commit
    blob_sha = hash_object(b"test content", "blob", write=True)
    entries = [TreeEntry(mode="100644", name="test.txt", sha1=blob_sha)]
    tree_sha = create_tree_object(entries)
    commit_sha = create_commit_object(tree_sha, message="Test commit")

    # Update branch to point to commit
    update_branch(commit_sha)

    # Should return the commit SHA
    result = get_current_commit()
    assert result == commit_sha


def test_update_branch(initialized_repo: Path) -> None:
    """Test updating branch pointer."""
    fake_commit_sha = "a" * 40

    update_branch(fake_commit_sha)

    # Should create the branch file
    branch_file = Path(".pygit/refs/heads/main")
    assert branch_file.exists()
    assert branch_file.read_text().strip() == fake_commit_sha


def test_get_current_tree_entries_no_commits(initialized_repo: Path) -> None:
    """Test getting tree entries when no commits exist."""
    result = get_current_tree_entries()
    assert result == {}


def test_get_current_tree_entries_with_commits(initialized_repo: Path) -> None:
    """Test getting tree entries from current commit."""
    # Create blobs
    blob1_sha = hash_object(b"content1", "blob", write=True)
    blob2_sha = hash_object(b"content2", "blob", write=True)

    # Create tree
    entries = [
        TreeEntry(mode="100644", name="file1.txt", sha1=blob1_sha),
        TreeEntry(mode="100644", name="file2.txt", sha1=blob2_sha),
    ]
    tree_sha = create_tree_object(entries)

    # Create commit
    commit_sha = create_commit_object(tree_sha, message="Test commit")
    update_branch(commit_sha)

    # Should return tree entries
    result = get_current_tree_entries()
    expected = {
        "file1.txt": blob1_sha,
        "file2.txt": blob2_sha,
    }
    assert result == expected


def test_init_repository_with_custom_path(temp_repo: Path) -> None:
    """Test initializing repository in a custom path."""
    custom_dir = temp_repo / "custom"
    custom_dir.mkdir()

    init_repository(str(custom_dir))

    # Should create .pygit in the custom directory
    pygit_dir = custom_dir / ".pygit"
    assert pygit_dir.exists()
    assert (pygit_dir / "objects").exists()
    assert (pygit_dir / "HEAD").exists()
