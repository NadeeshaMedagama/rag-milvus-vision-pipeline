"""GitHub repository reader service implementation."""
import os
import tempfile
import shutil
from typing import List
from pathlib import Path
import git

from interfaces import IRepositoryReader
from models import Document


class GitHubRepositoryReader(IRepositoryReader):
    """Service for reading markdown files from GitHub repositories."""

    def __init__(self, github_token: str = ""):
        """
        Initialize the repository reader.

        Args:
            github_token: Optional GitHub token for private repositories
        """
        self.github_token = github_token

    def clone_repository(self, repo_url: str) -> str:
        """
        Clone a repository and return the local path.

        Args:
            repo_url: URL of the repository to clone

        Returns:
            Path to the cloned repository (empty string if no URL provided)
        """
        # Skip cloning if URL is empty or None
        if not repo_url or repo_url.strip() == "":
            print("No repository URL provided - skipping repository cloning")
            return ""

        temp_dir = tempfile.mkdtemp(prefix="rag_repo_")

        try:
            # Add token to URL if provided
            if self.github_token:
                # Parse URL and insert token
                if "https://" in repo_url:
                    repo_url = repo_url.replace("https://", f"https://{self.github_token}@")

            print(f"Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, temp_dir, depth=1)
            print(f"Repository cloned to: {temp_dir}")
            return temp_dir
        except Exception as e:
            # Clean up on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise Exception(f"Failed to clone repository: {str(e)}")

    def get_markdown_files(self, repo_path: str) -> List[Document]:
        """
        Get all markdown files from the repository.

        Args:
            repo_path: Path to the repository

        Returns:
            List of Document objects (empty list if no repo path)
        """
        # Skip if no repository path provided
        if not repo_path or repo_path.strip() == "":
            print("No repository path provided - skipping markdown extraction")
            return []

        documents = []
        repo_path_obj = Path(repo_path)

        # Find all .md files recursively
        md_files = list(repo_path_obj.rglob("*.md"))

        print(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            try:
                # Skip files in .git directory
                if ".git" in str(md_file):
                    continue

                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get relative path from repo root
                relative_path = md_file.relative_to(repo_path_obj)

                document = Document(
                    content=content,
                    file_path=str(relative_path),
                    repository_url=repo_path,
                    metadata={
                        "file_size": md_file.stat().st_size,
                        "file_name": md_file.name
                    }
                )
                documents.append(document)
                print(f"Loaded: {relative_path}")
            except Exception as e:
                print(f"Error reading file {md_file}: {str(e)}")

        return documents

    def cleanup(self, repo_path: str) -> None:
        """
        Clean up the cloned repository.

        Args:
            repo_path: Path to the repository to clean up
        """
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            print(f"Cleaned up repository at: {repo_path}")

