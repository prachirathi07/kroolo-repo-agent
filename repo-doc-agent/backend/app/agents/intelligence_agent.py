from app.agents.state import AnalysisState
from app.services.llm_service import llm_service
from app.services.git_service import git_service
from app.core.logger import logger


def intelligence_agent(state: AnalysisState) -> AnalysisState:
    """
    Intelligence Agent - Uses LLM to generate insights
    
    Responsibilities:
    1. Summarize key code files
    2. Extract product features
    3. Generate use cases
    4. Create executive summary
    5. Generate marketing points
    
    Args:
        state: Current analysis state
    
    Returns:
        Updated state with LLM-generated insights
    """
    logger.info("[Intelligence Agent] Generating insights with LLM")
    state["current_step"] = "generating_insights"
    
    try:
        # Select key files to summarize (limit to avoid token limits)
        # Prioritize: entry points, largest files, most complex files
        key_files = sorted(
            state["file_analyses"],
            key=lambda x: (x.get("complexity", 0), x.get("lines_of_code", 0)),
            reverse=True
        )[:10]  # Top 10 files
        
        # Summarize key files
        file_summaries = []
        for file_analysis in key_files:
            try:
                file_path = file_analysis["path"]
                content = git_service.read_file_content(state["repo_id"], file_path)
                
                summary = llm_service.summarize_code(
                    content,
                    file_analysis.get("language", "Unknown"),
                    file_path
                )
                
                file_summaries.append({
                    "path": file_path,
                    "summary": summary,
                    "language": file_analysis.get("language"),
                    "functions": file_analysis.get("functions", []),
                    "classes": file_analysis.get("classes", [])
                })
                
                logger.debug(f"[Intelligence Agent] Summarized {file_path}")
                
            except Exception as e:
                logger.warning(f"[Intelligence Agent] Failed to summarize {file_path}: {str(e)}")
                continue
        
        state["file_summaries"] = file_summaries
        logger.info(f"[Intelligence Agent] Generated {len(file_summaries)} file summaries")
        
        # Extract features from code analysis
        code_analysis_summary = {
            "files": [
                {
                    "path": f["path"],
                    "language": f.get("language"),
                    "functions": f.get("functions", [])[:5],  # Top 5
                    "classes": f.get("classes", [])[:5]
                }
                for f in key_files
            ],
            "tech_stack": state["tech_stack"],
            "integrations": state["integrations"]
        }
        
        features = llm_service.extract_features_from_analysis(code_analysis_summary)
        state["features"] = features
        logger.info(f"[Intelligence Agent] Extracted {len(features)} features")
        
        # Generate use cases
        use_cases = llm_service.generate_use_cases(
            features,
            state["tech_stack"]
        )
        state["use_cases"] = use_cases
        logger.info(f"[Intelligence Agent] Generated {len(use_cases)} use cases")
        
        # Generate executive summary
        repo_info = {
            "name": state["repo_name"],
            "description": state["repo_description"],
            "tech_stack": state["tech_stack"],
            "features": features
        }
        
        executive_summary = llm_service.generate_executive_summary(repo_info)
        state["executive_summary"] = executive_summary
        logger.info("[Intelligence Agent] Generated executive summary")
        
        # Generate marketing points
        marketing_points = llm_service.generate_marketing_points(repo_info)
        state["marketing_points"] = marketing_points
        logger.info(f"[Intelligence Agent] Generated {len(marketing_points)} marketing points")
        
        # Generate product overview (combine summary and key features)
        product_overview = f"{executive_summary}\n\nKey Capabilities:\n"
        product_overview += "\n".join(f"• {feature}" for feature in features[:5])
        state["product_overview"] = product_overview
        
        state["current_step"] = "insights_generated"
        
        return state
        
    except Exception as e:
        error_msg = f"Intelligence agent failed: {str(e)}"
        logger.error(f"[Intelligence Agent] {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "failed"
        return state
