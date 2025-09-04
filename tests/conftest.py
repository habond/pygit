"""
Pytest configuration and shared fixtures.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_repo() -> Generator[Path, None, None]:
    """
    Create a temporary directory and change to it for testing.
    
    This isolates each test in its own directory, so .pygit operations
    don't interfere with each other or the actual project.
    """
    original_cwd = os.getcwd()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)
        try:
            yield temp_path
        finally:
            os.chdir(original_cwd)


@pytest.fixture
def initialized_repo(temp_repo: Path) -> Path:
    """
    Create a temporary directory with an initialized pygit repository.
    """
    from src.repository import init_repository
    
    init_repository()
    return temp_repo


@pytest.fixture
def sample_file(temp_repo: Path) -> Path:
    """Create a sample file for testing."""
    sample_path = temp_repo / "sample.txt"
    sample_path.write_text("Hello, PyGit testing!")
    return sample_path


@pytest.fixture
def multiple_files(temp_repo: Path) -> list[Path]:
    """Create multiple sample files for testing."""
    files = []
    for i in range(3):
        file_path = temp_repo / f"file{i}.txt"
        file_path.write_text(f"Content of file {i}")
        files.append(file_path)
    return files