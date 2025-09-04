"""
End-to-end integration tests for PyGit.

These tests simulate real user workflows.
"""

from pathlib import Path

from src.repository import init_repository, get_current_commit
from src.commands import add_command, commit_command, status_command
from src.index import read_index
from src.objects import read_object, parse_tree_object


def test_basic_workflow(temp_repo: Path, capsys) -> None:
    """Test a complete basic git workflow."""
    # 1. Initialize repository
    init_repository()
    assert Path(".pygit").exists()
    
    # 2. Create some files
    file1 = Path("README.md")
    file1.write_text("# My Project\n\nThis is a test project.")
    
    file2 = Path("main.py")
    file2.write_text('print("Hello, World!")')
    
    # 3. Check status - should show untracked files
    status_command()
    captured = capsys.readouterr()
    assert "README.md" in captured.out
    assert "main.py" in captured.out
    assert "no files staged" in captured.out
    
    # 4. Add files to staging area
    add_command("README.md")
    add_command("main.py")
    
    # 5. Check status - should show staged files
    status_command()
    captured = capsys.readouterr()
    assert "README.md" in captured.out
    assert "main.py" in captured.out
    assert "Staged files:" in captured.out
    
    # 6. Create first commit
    commit_command("Initial commit")
    captured = capsys.readouterr()
    assert "Created commit" in captured.out
    
    # 7. Check that index is cleared
    assert read_index() == {}
    
    # 8. Verify commit exists and has correct content
    commit_sha = get_current_commit()
    assert commit_sha is not None
    
    obj_type, size, content = read_object(commit_sha)
    assert obj_type == "commit"
    commit_text = content.decode()
    assert "Initial commit" in commit_text
    assert "tree " in commit_text


def test_multiple_commits_workflow(temp_repo: Path, capsys) -> None:
    """Test workflow with multiple commits."""
    # Initialize and create first commit
    init_repository()
    
    file1 = Path("feature.py")
    file1.write_text("def feature(): pass")
    add_command("feature.py")
    commit_command("Add feature")
    
    first_commit = get_current_commit()
    assert first_commit is not None
    
    # Create second commit
    file2 = Path("test.py")
    file2.write_text("def test_feature(): pass")
    add_command("test.py")
    commit_command("Add tests")
    
    second_commit = get_current_commit()
    assert second_commit is not None
    assert second_commit != first_commit
    
    # Verify second commit has parent
    obj_type, size, content = read_object(second_commit)
    commit_text = content.decode()
    assert f"parent {first_commit}" in commit_text
    assert "Add tests" in commit_text


def test_tree_structure_preservation(temp_repo: Path) -> None:
    """Test that tree structure is correctly preserved across commits."""
    init_repository()
    
    # Create and commit first file
    file1 = Path("file1.txt")
    file1.write_text("Content 1")
    add_command("file1.txt")
    commit_command("Add file1")
    
    # Create and commit second file
    file2 = Path("file2.txt") 
    file2.write_text("Content 2")
    add_command("file2.txt")
    commit_command("Add file2")
    
    # Verify both files are in the final commit's tree
    commit_sha = get_current_commit()
    assert commit_sha is not None
    
    # Get tree from commit
    obj_type, size, content = read_object(commit_sha)
    commit_text = content.decode()
    
    # Extract tree SHA
    tree_line = [line for line in commit_text.split('\n') if line.startswith('tree ')][0]
    tree_sha = tree_line.split()[1]
    
    # Parse tree
    obj_type, size, tree_content = read_object(tree_sha)
    entries = parse_tree_object(tree_content)
    
    # Should have both files
    filenames = [entry['name'] for entry in entries]
    assert "file1.txt" in filenames
    assert "file2.txt" in filenames


def test_empty_commit_prevention(temp_repo: Path, capsys) -> None:
    """Test that commits are prevented when nothing is staged."""
    init_repository()
    
    # Try to commit with nothing staged
    commit_command("Empty commit")
    
    captured = capsys.readouterr()
    assert "no files staged" in captured.out
    
    # Should not create any commit
    assert get_current_commit() is None


def test_file_modification_workflow(temp_repo: Path) -> None:
    """Test workflow involving file modifications."""
    init_repository()
    
    # Create and commit initial version
    test_file = Path("evolving.txt")
    test_file.write_text("Version 1")
    add_command("evolving.txt")
    commit_command("Initial version")
    
    first_commit = get_current_commit()
    
    # Modify and commit again
    test_file.write_text("Version 2")
    add_command("evolving.txt")
    commit_command("Updated version")
    
    second_commit = get_current_commit()
    
    # Verify different commits
    assert first_commit != second_commit
    
    # Verify second commit has the new content
    # (This would require implementing checkout to fully verify,
    # but we can at least check the commit chain is correct)
    obj_type, size, content = read_object(second_commit)
    commit_text = content.decode()
    assert f"parent {first_commit}" in commit_text