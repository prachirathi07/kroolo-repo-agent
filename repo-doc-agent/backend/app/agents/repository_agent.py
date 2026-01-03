from app.agents.state import AnalysisState
from app.services.git_service import git_service
from app.core.logger import logger


def repository_agent(state: AnalysisState) -> AnalysisState:
    """
    Repository Agent - Clones repository and detects changes
    
    Responsibilities:
    1. Clone repository (or pull if exists)
    2. Get current commit hash
    3. Detect file changes (if incremental)
    4. Get file tree
    5. Filter files by constraints
    
    Args:
        state: Current analysis state
    
    Returns:
        Updated state with repository info and file list
    """
    logger.info(f"[Repository Agent] Starting for repo: {state['repo_url']}")
    state["current_step"] = "cloning_repository"
    
    try:
        # Get repo info from GitHub/GitLab API
        repo_info = git_service.get_repo_info_from_github(
            state["repo_url"],
            state.get("auth_token")
        )
        state["repo_name"] = repo_info["name"]
        state["repo_description"] = repo_info["description"]
        
        # Clone or pull repository
        if state.get("is_incremental") and state.get("local_path"):
            logger.info("[Repository Agent] Pulling latest changes...")
            new_commit, has_changes = git_service.pull_latest_changes(state["repo_id"])
            state["current_commit_hash"] = new_commit
            
            if not has_changes:
                logger.info("[Repository Agent] No changes detected")
                state["warnings"].append("No changes detected in repository")
                return state
            
            # Get diff
            if state.get("previous_commit_hash"):
                changes = git_service.get_commit_diff(
                    state["repo_id"],
                    state["previous_commit_hash"],
                    new_commit
                )
                state["changed_files"] = changes
                logger.info(f"[Repository Agent] Changes: {len(changes['added'])} added, "
                          f"{len(changes['modified'])} modified, {len(changes['deleted'])} deleted")
        else:
            logger.info("[Repository Agent] Cloning repository...")
            local_path, commit_hash = git_service.clone_repository(
                state["repo_url"],
                state["repo_id"],
                state["branch"],
                state.get("auth_token")
            )
            state["local_path"] = local_path
            state["current_commit_hash"] = commit_hash
        
        # Get file tree
        logger.info("[Repository Agent] Building file tree...")
        files = git_service.get_file_tree(state["repo_id"])
        
        # Filter files to analyze
        if state.get("is_incremental") and state.get("changed_files"):
            # Only analyze changed files
            changed_paths = set(
                state["changed_files"]["added"] + 
                state["changed_files"]["modified"]
            )
            files = [f for f in files if f["path"] in changed_paths]
            logger.info(f"[Repository Agent] Incremental mode: analyzing {len(files)} changed files")
        
        state["files"] = files
        state["total_files"] = len(files)
        state["total_size_bytes"] = sum(f["size"] for f in files)
        
        logger.info(f"[Repository Agent] Found {len(files)} files to analyze")
        
        # Build file tree structure
        file_tree = {}
        for file_info in files:
            parts = file_info["path"].split('/')
            current = file_tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = file_info
        
        state["file_tree"] = file_tree
        state["current_step"] = "repository_cloned"
        
        return state
        
    except Exception as e:
        error_msg = f"Repository agent failed: {str(e)}"
        logger.error(f"[Repository Agent] {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "failed"
        return state
