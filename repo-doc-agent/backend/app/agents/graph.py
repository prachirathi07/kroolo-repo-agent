from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AnalysisState, create_initial_state
from app.agents.repository_agent import repository_agent
from app.agents.code_agent import code_analysis_agent
from app.agents.intelligence_agent import intelligence_agent
from app.agents.doc_generator import documentation_generator_agent
from app.core.logger import logger


def should_continue(state: AnalysisState) -> str:
    """
    Conditional routing - determine next step based on state
    
    Args:
        state: Current state
    
    Returns:
        Next node name or END
    """
    # Check for errors
    if state["errors"]:
        logger.error(f"[Graph] Errors detected: {state['errors']}")
        return END
    
    # Check current step
    current_step = state.get("current_step", "")
    
    if current_step == "failed":
        return END
    elif current_step == "repository_cloned":
        # Check if we have files to analyze
        if state["total_files"] == 0:
            logger.warning("[Graph] No files to analyze")
            state["warnings"].append("No analyzable files found")
            return END
        return "code_analysis"
    elif current_step == "code_analyzed":
        return "intelligence"
    elif current_step == "insights_generated":
        return "documentation"
    elif current_step == "completed":
        return END
    else:
        logger.warning(f"[Graph] Unknown step: {current_step}")
        return END


def create_analysis_graph():
    """
    Create the LangGraph workflow for repository analysis
    
    Returns:
        Compiled graph
    """
    # Create graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes (agents)
    workflow.add_node("repository", repository_agent)
    workflow.add_node("code_analysis", code_analysis_agent)
    workflow.add_node("intelligence", intelligence_agent)
    workflow.add_node("documentation", documentation_generator_agent)
    
    # Set entry point
    workflow.set_entry_point("repository")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "repository",
        should_continue,
        {
            "code_analysis": "code_analysis",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "code_analysis",
        should_continue,
        {
            "intelligence": "intelligence",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "intelligence",
        should_continue,
        {
            "documentation": "documentation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "documentation",
        should_continue,
        {
            END: END
        }
    )
    
    # Compile with checkpointing
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    logger.info("[Graph] Analysis workflow compiled successfully")
    
    return app


# Create global graph instance
analysis_graph = create_analysis_graph()


async def run_analysis(
    repo_url: str,
    repo_id: str,
    branch: str = "main",
    auth_token: str = None,
    is_incremental: bool = False,
    previous_commit: str = None
) -> AnalysisState:
    """
    Run the complete analysis workflow
    
    Args:
        repo_url: Repository URL
        repo_id: Unique repository ID
        branch: Git branch
        auth_token: Authentication token
        is_incremental: Whether this is incremental update
        previous_commit: Previous commit hash
    
    Returns:
        Final state with all analysis results
    """
    logger.info(f"[Graph] Starting analysis for {repo_url}")
    
    # Create initial state
    initial_state = create_initial_state(
        repo_url=repo_url,
        repo_id=repo_id,
        branch=branch,
        auth_token=auth_token,
        is_incremental=is_incremental,
        previous_commit=previous_commit
    )
    
    # Run graph
    config = {"configurable": {"thread_id": repo_id}}
    
    try:
        # Execute workflow
        final_state = None
        for state in analysis_graph.stream(initial_state, config):
            # state is a dict with node name as key
            for node_name, node_state in state.items():
                logger.info(f"[Graph] Completed node: {node_name}, Step: {node_state.get('current_step')}")
                final_state = node_state
        
        logger.info(f"[Graph] Analysis complete. Status: {final_state.get('current_step')}")
        
        return final_state
        
    except Exception as e:
        logger.error(f"[Graph] Analysis failed: {str(e)}")
        raise Exception(f"Analysis workflow failed: {str(e)}")
