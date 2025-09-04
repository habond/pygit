"""
Tests for the commands module.
"""

from pathlib import Path
from io import StringIO
import sys

from src.commands import (
    hash_object_command,
    cat_file_command,
    add_command,
    status_command,
    commit_command,
    checkout_command,
    log_command,
)
from src.repository import init_repository
from src.objects import hash_object, read_object


def test_hash_object_command_file_not_found(temp_repo: Path, capsys) -> None:
    """Test hash-object command with non-existent file."""
    hash_object_command("nonexistent.txt", write=False)
    
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_hash_object_command_success(sample_file: Path, capsys) -> None:
    """Test hash-object command with existing file."""
    hash_object_command(str(sample_file), write=False)
    
    captured = capsys.readouterr()
    output_hash = captured.out.strip()
    
    # Should output a valid SHA-1 hash
    assert len(output_hash) == 40
    assert all(c in "0123456789abcdef" for c in output_hash)


def test_hash_object_command_with_write(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test hash-object command with write flag."""
    hash_object_command(str(sample_file), write=True)
    
    captured = capsys.readouterr()
    output_hash = captured.out.strip()
    
    # Should be able to read the object back
    obj_type, size, content = read_object(output_hash)
    assert obj_type == "blob"
    assert content == sample_file.read_bytes()


def test_cat_file_command_not_found(initialized_repo: Path, capsys) -> None:
    """Test cat-file command with non-existent object."""
    fake_hash = "a" * 40
    cat_file_command(fake_hash)
    
    captured = capsys.readouterr()
    assert "Error:" in captured.out


def test_cat_file_command_show_content(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test cat-file command showing content."""
    # Create a blob first
    blob_hash = hash_object(sample_file.read_bytes(), "blob", write=True)
    
    cat_file_command(blob_hash)
    
    captured = capsys.readouterr()
    assert captured.out == sample_file.read_text()


def test_cat_file_command_show_type(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test cat-file command showing type."""
    blob_hash = hash_object(sample_file.read_bytes(), "blob", write=True)
    
    cat_file_command(blob_hash, show_type=True)
    
    captured = capsys.readouterr()
    assert captured.out.strip() == "blob"


def test_cat_file_command_show_size(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test cat-file command showing size."""
    blob_hash = hash_object(sample_file.read_bytes(), "blob", write=True)
    
    cat_file_command(blob_hash, show_size=True)
    
    captured = capsys.readouterr()
    assert captured.out.strip() == str(len(sample_file.read_bytes()))


def test_add_command(initialized_repo: Path, sample_file: Path) -> None:
    """Test add command."""
    from src.index import read_index
    
    # Initially index should be empty
    assert read_index() == {}
    
    # Add file
    add_command(str(sample_file))
    
    # Should update index
    index = read_index()
    assert str(sample_file) in index


def test_status_command_empty(initialized_repo: Path, capsys) -> None:
    """Test status command with empty repository."""
    status_command()
    
    captured = capsys.readouterr()
    assert "no files staged" in captured.out
    assert "(none)" in captured.out


def test_status_command_with_staged_files(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test status command with staged files."""
    add_command(str(sample_file))
    
    status_command()
    
    captured = capsys.readouterr()
    assert "Staged files:" in captured.out
    assert str(sample_file) in captured.out


def test_status_command_with_untracked_files(initialized_repo: Path, capsys) -> None:
    """Test status command with untracked files."""
    # Create a file but don't stage it
    untracked_file = Path("untracked.txt")
    untracked_file.write_text("untracked content")
    
    status_command()
    
    captured = capsys.readouterr()
    assert "Untracked files:" in captured.out
    assert "untracked.txt" in captured.out


def test_commit_command_no_staged_files(initialized_repo: Path, capsys) -> None:
    """Test commit command with no staged files."""
    commit_command("Test commit")
    
    captured = capsys.readouterr()
    assert "no files staged" in captured.out


def test_commit_command_success(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test successful commit command."""
    # Stage a file
    add_command(str(sample_file))
    
    # Commit it
    commit_command("Test commit")
    
    captured = capsys.readouterr()
    assert "Created commit" in captured.out
    
    # Should clear the index
    from src.index import read_index
    assert read_index() == {}


def test_commit_command_with_parent(initialized_repo: Path, multiple_files: list[Path], capsys) -> None:
    """Test commit command creating a commit with parent."""
    # Create first commit
    add_command(str(multiple_files[0]))
    commit_command("First commit")
    
    # Create second commit
    add_command(str(multiple_files[1]))
    commit_command("Second commit")
    
    captured = capsys.readouterr()
    assert "Created commit" in captured.out
    assert "Parent:" in captured.out


def test_checkout_command_invalid_commit(initialized_repo: Path, capsys) -> None:
    """Test checkout command with invalid commit hash."""
    fake_hash = "a" * 40
    checkout_command(fake_hash)
    
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_checkout_command_success(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test successful checkout command."""
    # Create a commit first
    add_command(str(sample_file))
    commit_command("Test commit")
    captured = capsys.readouterr()
    
    # Extract commit hash from output
    lines = captured.out.split("\n")
    commit_line = next(line for line in lines if "Created commit" in line)
    commit_hash = commit_line.split()[-1]
    
    # Modify the file
    sample_file.write_text("modified content")
    
    # Checkout the commit
    checkout_command(commit_hash)
    
    captured = capsys.readouterr()
    assert f"Checked out commit {commit_hash}" in captured.out
    
    # File should be restored to original content
    assert sample_file.read_text() == "Hello, PyGit testing!"


def test_checkout_command_not_a_commit(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test checkout command with a blob hash instead of commit."""
    # Create a blob
    blob_hash = hash_object(sample_file.read_bytes(), "blob", write=True)
    
    checkout_command(blob_hash)
    
    captured = capsys.readouterr()
    assert "is not a commit object" in captured.out


def test_log_command_no_commits(initialized_repo: Path, capsys) -> None:
    """Test log command with no commits."""
    log_command()
    
    captured = capsys.readouterr()
    assert "No commits found" in captured.out


def test_log_command_single_commit(initialized_repo: Path, sample_file: Path, capsys) -> None:
    """Test log command with single commit."""
    # Create a commit
    add_command(str(sample_file))
    commit_command("Initial commit")
    
    # Clear previous output
    capsys.readouterr()
    
    # Run log command
    log_command()
    
    captured = capsys.readouterr()
    assert "commit " in captured.out
    assert "Author:" in captured.out
    assert "Initial commit" in captured.out


def test_log_command_multiple_commits(initialized_repo: Path, multiple_files: list[Path], capsys) -> None:
    """Test log command with multiple commits showing history."""
    # Create first commit
    add_command(str(multiple_files[0]))
    commit_command("First commit")
    
    # Create second commit  
    add_command(str(multiple_files[1]))
    commit_command("Second commit")
    
    # Clear previous output
    capsys.readouterr()
    
    # Run log command
    log_command()
    
    captured = capsys.readouterr()
    
    # Should show both commits, most recent first
    lines = captured.out.split('\n')
    commit_lines = [line for line in lines if line.startswith('commit ')]
    
    # Should have exactly 2 commits
    assert len(commit_lines) == 2
    
    # Should contain both commit messages
    assert "Second commit" in captured.out
    assert "First commit" in captured.out
    
    # Most recent commit should appear first
    first_commit_pos = captured.out.find("First commit")
    second_commit_pos = captured.out.find("Second commit")
    assert second_commit_pos < first_commit_pos