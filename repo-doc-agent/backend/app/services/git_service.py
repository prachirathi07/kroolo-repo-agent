import os
import shutil
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import git
from git import Repo
from github import Github
from gitlab import Gitlab
from app.core.config import settings
from app.core.logger import logger


class GitService:
    """Service for Git repository operations"""
    
    def __init__(self):
        self.temp_dir = settings.TEMP_REPOS_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _get_repo_name(self, url: str) -> str:
        """Extract repository name from URL"""
        # Remove .git suffix and get last part
        name = url.rstrip('/').split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]
        return name
    
    def _get_local_path(self, repo_id: str) -> str:
        """Get local path for cloned repository"""
        return os.path.join(self.temp_dir, repo_id)
    
    def clone_repository(
        self, 
        url: str, 
        repo_id: str, 
        branch: str = "main",
        auth_token: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Clone a repository
        
        Args:
            url: Repository URL
            repo_id: Unique repository ID
            branch: Branch to clone
            auth_token: Authentication token for private repos
        
        Returns:
            Tuple of (local_path, commit_hash)
        """
        local_path = self._get_local_path(repo_id)
        
        # Remove existing directory if it exists
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        
        try:
            # Prepare URL with authentication
            clone_url = url
            if auth_token:
                # Inject token into URL
                if "github.com" in url:
                    clone_url = url.replace("https://", f"https://{auth_token}@")
                elif "gitlab.com" in url:
                    clone_url = url.replace("https://", f"https://oauth2:{auth_token}@")
            
            logger.info(f"Cloning repository: {url} to {local_path}")
            
            # Clone repository
            repo = Repo.clone_from(
                clone_url,
                local_path,
                branch=branch,
                depth=1  # Shallow clone for speed
            )
            
            # Get current commit hash
            commit_hash = repo.head.commit.hexsha
            
            logger.info(f"Successfully cloned repository. Commit: {commit_hash}")
            
            return local_path, commit_hash
            
        except git.GitCommandError as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def pull_latest_changes(self, repo_id: str) -> Tuple[str, bool]:
        """
        Pull latest changes from repository
        
        Args:
            repo_id: Repository ID
        
        Returns:
            Tuple of (new_commit_hash, has_changes)
        """
        local_path = self._get_local_path(repo_id)
        
        if not os.path.exists(local_path):
            raise Exception(f"Repository not found at {local_path}")
        
        try:
            repo = Repo(local_path)
            old_commit = repo.head.commit.hexsha
            
            # Pull latest changes
            origin = repo.remotes.origin
            origin.pull()
            
            new_commit = repo.head.commit.hexsha
            has_changes = old_commit != new_commit
            
            logger.info(f"Pulled changes. Old: {old_commit[:8]}, New: {new_commit[:8]}, Changed: {has_changes}")
            
            return new_commit, has_changes
            
        except git.GitCommandError as e:
            logger.error(f"Failed to pull changes: {str(e)}")
            raise Exception(f"Failed to pull changes: {str(e)}")
    
    def get_commit_diff(
        self, 
        repo_id: str, 
        old_commit: str, 
        new_commit: str
    ) -> Dict[str, List[str]]:
        """
        Get diff between two commits
        
        Args:
            repo_id: Repository ID
            old_commit: Old commit hash
            new_commit: New commit hash
        
        Returns:
            Dict with added, modified, deleted files
        """
        local_path = self._get_local_path(repo_id)
        
        try:
            repo = Repo(local_path)
            
            # Get diff between commits
            old = repo.commit(old_commit)
            new = repo.commit(new_commit)
            
            diff = old.diff(new)
            
            changes = {
                "added": [],
                "modified": [],
                "deleted": []
            }
            
            for change in diff:
                if change.new_file:
                    changes["added"].append(change.b_path)
                elif change.deleted_file:
                    changes["deleted"].append(change.a_path)
                elif change.renamed_file:
                    changes["modified"].append(change.b_path)
                else:
                    changes["modified"].append(change.b_path)
            
            logger.info(f"Diff: {len(changes['added'])} added, {len(changes['modified'])} modified, {len(changes['deleted'])} deleted")
            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to get diff: {str(e)}")
            raise Exception(f"Failed to get diff: {str(e)}")
    
    def get_file_tree(self, repo_id: str) -> List[Dict[str, any]]:
        """
        Get file tree structure
        
        Args:
            repo_id: Repository ID
        
        Returns:
            List of file info dicts
        """
        local_path = self._get_local_path(repo_id)
        files = []
        
        # Excluded directories
        excluded_dirs = {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.venv', 'dist', 'build'}
        
        for root, dirs, filenames in os.walk(local_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, local_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Skip files larger than max size
                if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.warning(f"Skipping large file: {relative_path} ({file_size} bytes)")
                    continue
                
                files.append({
                    "path": relative_path,
                    "size": file_size,
                    "extension": Path(filename).suffix
                })
        
        logger.info(f"Found {len(files)} files in repository")
        
        # Check file count limit
        if len(files) > settings.MAX_FILES:
            logger.warning(f"Repository has {len(files)} files, exceeding limit of {settings.MAX_FILES}")
            # Return only first N files
            return files[:settings.MAX_FILES]
        
        return files
    
    def calculate_file_hash(self, repo_id: str, file_path: str) -> str:
        """
        Calculate SHA256 hash of a file
        
        Args:
            repo_id: Repository ID
            file_path: Relative file path
        
        Returns:
            SHA256 hash string
        """
        local_path = self._get_local_path(repo_id)
        full_path = os.path.join(local_path, file_path)
        
        sha256_hash = hashlib.sha256()
        
        with open(full_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def read_file_content(self, repo_id: str, file_path: str) -> str:
        """
        Read file content
        
        Args:
            repo_id: Repository ID
            file_path: Relative file path
        
        Returns:
            File content as string
        """
        local_path = self._get_local_path(repo_id)
        full_path = os.path.join(local_path, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(full_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def cleanup_repository(self, repo_id: str):
        """
        Delete cloned repository
        
        Args:
            repo_id: Repository ID
        """
        local_path = self._get_local_path(repo_id)
        
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
            logger.info(f"Cleaned up repository: {local_path}")
    
    def get_repo_info_from_github(self, url: str, token: Optional[str] = None) -> Dict[str, str]:
        """
        Get repository info from GitHub API
        
        Args:
            url: GitHub repository URL
            token: GitHub personal access token
        
        Returns:
            Dict with name and description
        """
        try:
            # Extract owner and repo name
            parts = url.rstrip('/').split('/')
            owner = parts[-2]
            repo_name = parts[-1].replace('.git', '')
            
            # Use token if provided, otherwise use from settings
            auth_token = token or settings.GITHUB_TOKEN
            
            if auth_token:
                g = Github(auth_token)
            else:
                g = Github()
            
            repo = g.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "description": repo.description or ""
            }
            
        except Exception as e:
            logger.warning(f"Failed to get GitHub repo info: {str(e)}")
            return {"name": self._get_repo_name(url), "description": ""}


# Global instance
git_service = GitService()
