from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages


class AnalysisState(TypedDict):
    """
    State schema for LangGraph analysis workflow
    
    This state is passed between all agent nodes and accumulates
    information throughout the analysis process.
    """
    
    # Repository Info
    repo_url: str
    repo_id: str
    repo_name: str
    repo_description: str
    branch: str
    auth_token: Optional[str]
    
    # Git Info
    local_path: Optional[str]
    current_commit_hash: Optional[str]
    previous_commit_hash: Optional[str]
    
    # File Information
    files: List[Dict]  # List of file info dicts
    file_tree: Dict  # Structured file tree
    total_files: int
    total_size_bytes: int
    
    # Code Analysis Results
    file_analyses: List[Dict]  # Analysis for each file
    tech_stack: Dict[str, List[str]]  # Categorized tech stack
    total_lines_of_code: int
    total_complexity: int
    
    # LLM-Generated Insights
    file_summaries: List[Dict]  # LLM summaries for key files
    features: List[str]  # Extracted features
    use_cases: List[str]  # Generated use cases
    integrations: List[str]  # Identified integrations
    
    # Final Documentation
    executive_summary: Optional[str]
    product_overview: Optional[str]
    architecture_diagram: Optional[str]  # Mermaid syntax
    marketing_points: List[str]
    
    # Workflow Control
    current_step: str  # Current processing step
    is_incremental: bool  # Whether this is an incremental update
    changed_files: Optional[Dict]  # For incremental updates
    
    # Error Handling
    errors: List[str]
    warnings: List[str]
    
    # Messages (for LangGraph message passing)
    messages: Annotated[List, add_messages]


def create_initial_state(
    repo_url: str,
    repo_id: str,
    branch: str = "main",
    auth_token: Optional[str] = None,
    is_incremental: bool = False,
    previous_commit: Optional[str] = None
) -> AnalysisState:
    """
    Create initial state for analysis
    
    Args:
        repo_url: Repository URL
        repo_id: Unique repository ID
        branch: Git branch
        auth_token: Authentication token
        is_incremental: Whether this is incremental update
        previous_commit: Previous commit hash (for incremental)
    
    Returns:
        Initial AnalysisState
    """
    return AnalysisState(
        # Repository Info
        repo_url=repo_url,
        repo_id=repo_id,
        repo_name="",
        repo_description="",
        branch=branch,
        auth_token=auth_token,
        
        # Git Info
        local_path=None,
        current_commit_hash=None,
        previous_commit_hash=previous_commit,
        
        # File Information
        files=[],
        file_tree={},
        total_files=0,
        total_size_bytes=0,
        
        # Code Analysis
        file_analyses=[],
        tech_stack={},
        total_lines_of_code=0,
        total_complexity=0,
        
        # LLM Insights
        file_summaries=[],
        features=[],
        use_cases=[],
        integrations=[],
        
        # Documentation
        executive_summary=None,
        product_overview=None,
        architecture_diagram=None,
        marketing_points=[],
        
        # Workflow
        current_step="initialized",
        is_incremental=is_incremental,
        changed_files=None,
        
        # Errors
        errors=[],
        warnings=[],
        
        # Messages
        messages=[]
    )
