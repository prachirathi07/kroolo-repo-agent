from app.agents.state import AnalysisState
from app.services.git_service import git_service
from app.services.parser_service import parser_service
from app.core.logger import logger


def code_analysis_agent(state: AnalysisState) -> AnalysisState:
    """
    Code Analysis Agent - Parses and analyzes code files
    
    Responsibilities:
    1. Parse each file using appropriate parser
    2. Extract functions, classes, imports
    3. Calculate code metrics
    4. Identify tech stack
    5. Aggregate statistics
    
    Args:
        state: Current analysis state
    
    Returns:
        Updated state with code analysis results
    """
    logger.info(f"[Code Analysis Agent] Analyzing {len(state['files'])} files")
    state["current_step"] = "analyzing_code"
    
    try:
        file_analyses = []
        total_loc = 0
        total_complexity = 0
        
        # Analyze each file
        for file_info in state["files"]:
            file_path = file_info["path"]
            
            # Skip non-code files
            if not parser_service.detect_language(file_path):
                continue
            
            try:
                # Read file content
                content = git_service.read_file_content(state["repo_id"], file_path)
                
                # Parse file
                analysis = parser_service.parse_file(file_path, content)
                analysis["path"] = file_path
                analysis["size"] = file_info["size"]
                
                file_analyses.append(analysis)
                
                total_loc += analysis.get("lines_of_code", 0)
                total_complexity += analysis.get("complexity", 0)
                
                logger.debug(f"[Code Analysis Agent] Analyzed {file_path}: "
                           f"{analysis.get('lines_of_code', 0)} LOC, "
                           f"{len(analysis.get('functions', []))} functions")
                
            except Exception as e:
                logger.warning(f"[Code Analysis Agent] Failed to analyze {file_path}: {str(e)}")
                state["warnings"].append(f"Failed to analyze {file_path}")
                continue
        
        state["file_analyses"] = file_analyses
        state["total_lines_of_code"] = total_loc
        state["total_complexity"] = total_complexity
        
        logger.info(f"[Code Analysis Agent] Analyzed {len(file_analyses)} files successfully")
        logger.info(f"[Code Analysis Agent] Total LOC: {total_loc}, Complexity: {total_complexity}")
        
        # Categorize tech stack
        tech_stack = parser_service.categorize_tech_stack(file_analyses)
        state["tech_stack"] = tech_stack
        
        logger.info(f"[Code Analysis Agent] Tech Stack: {tech_stack}")
        
        # Identify integrations
        integrations = parser_service.identify_frameworks(
            [imp for analysis in file_analyses for imp in analysis.get('imports', [])]
        )
        state["integrations"] = integrations
        
        logger.info(f"[Code Analysis Agent] Identified {len(integrations)} integrations")
        
        state["current_step"] = "code_analyzed"
        
        return state
        
    except Exception as e:
        error_msg = f"Code analysis agent failed: {str(e)}"
        logger.error(f"[Code Analysis Agent] {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "failed"
        return state
