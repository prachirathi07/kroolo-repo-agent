from app.agents.state import AnalysisState
from app.core.logger import logger


def documentation_generator_agent(state: AnalysisState) -> AnalysisState:
    """
    Documentation Generator Agent - Compiles final documentation
    
    Responsibilities:
    1. Generate architecture diagram (Mermaid)
    2. Compile all insights into structured documentation
    3. Format for web display
    4. Prepare for database storage
    
    Args:
        state: Current analysis state
    
    Returns:
        Updated state with final documentation
    """
    logger.info("[Documentation Generator] Compiling final documentation")
    state["current_step"] = "generating_documentation"
    
    try:
        # Generate architecture diagram (Mermaid syntax)
        architecture_diagram = generate_architecture_diagram(state)
        state["architecture_diagram"] = architecture_diagram
        
        logger.info("[Documentation Generator] Generated architecture diagram")
        
        # All documentation is already in state, just mark as complete
        state["current_step"] = "completed"
        
        logger.info("[Documentation Generator] Documentation generation complete")
        
        return state
        
    except Exception as e:
        error_msg = f"Documentation generator failed: {str(e)}"
        logger.error(f"[Documentation Generator] {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "failed"
        return state


def generate_architecture_diagram(state: AnalysisState) -> str:
    """
    Generate Mermaid architecture diagram
    
    Args:
        state: Analysis state
    
    Returns:
        Mermaid diagram syntax
    """
    tech_stack = state["tech_stack"]
    integrations = state["integrations"]
    
    # Build diagram
    diagram = "graph TD\n"
    
    # Add layers based on tech stack
    layers = []
    
    # Frontend layer
    frontend_frameworks = [fw for fw in tech_stack.get("frameworks", []) 
                          if any(x in fw.lower() for x in ["react", "vue", "angular", "next", "svelte"])]
    if frontend_frameworks:
        layers.append("Frontend")
        diagram += f"    Frontend[\"🎨 Frontend<br/>{', '.join(frontend_frameworks)}\"]\n"
    
    # Backend layer
    backend_frameworks = [fw for fw in tech_stack.get("frameworks", []) 
                         if any(x in fw.lower() for x in ["django", "flask", "fastapi", "express", "spring", "laravel"])]
    if backend_frameworks:
        layers.append("Backend")
        diagram += f"    Backend[\"⚙️ Backend<br/>{', '.join(backend_frameworks)}\"]\n"
    elif tech_stack.get("languages"):
        layers.append("Backend")
        diagram += f"    Backend[\"⚙️ Backend<br/>{', '.join(tech_stack['languages'][:2])}\"]\n"
    
    # Database layer
    if tech_stack.get("databases"):
        layers.append("Database")
        diagram += f"    Database[(\"💾 Database<br/>{', '.join(tech_stack['databases'])}\" )]\n"
    
    # External integrations
    if integrations:
        layers.append("Integrations")
        diagram += f"    Integrations[\"🔌 Integrations<br/>{', '.join(integrations[:3])}\"]\n"
    
    # Add connections
    if "Frontend" in layers and "Backend" in layers:
        diagram += "    Frontend --> Backend\n"
    if "Backend" in layers and "Database" in layers:
        diagram += "    Backend --> Database\n"
    if "Backend" in layers and "Integrations" in layers:
        diagram += "    Backend --> Integrations\n"
    
    # Style
    diagram += "\n    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px\n"
    diagram += "    classDef backend fill:#68a063,stroke:#333,stroke-width:2px\n"
    diagram += "    classDef database fill:#f39c12,stroke:#333,stroke-width:2px\n"
    diagram += "    classDef integration fill:#9b59b6,stroke:#333,stroke-width:2px\n"
    
    if "Frontend" in layers:
        diagram += "    class Frontend frontend\n"
    if "Backend" in layers:
        diagram += "    class Backend backend\n"
    if "Database" in layers:
        diagram += "    class Database database\n"
    if "Integrations" in layers:
        diagram += "    class Integrations integration\n"
    
    return diagram
