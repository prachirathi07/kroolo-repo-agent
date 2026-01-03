import ast
import re
from typing import Dict, List, Optional
from pathlib import Path
from app.core.logger import logger


class ParserService:
    """Service for parsing code files"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'React TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect programming language from file extension
        
        Args:
            file_path: File path
        
        Returns:
            Language name or None
        """
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(ext)
    
    def parse_file(self, file_path: str, content: str) -> Dict:
        """
        Parse a code file and extract information
        
        Args:
            file_path: File path
            content: File content
        
        Returns:
            Dict with parsed information
        """
        language = self.detect_language(file_path)
        
        if not language:
            return {
                "language": "Unknown",
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity": 0,
                "lines_of_code": len(content.split('\n'))
            }
        
        # Route to appropriate parser
        if language == "Python":
            return self._parse_python(content)
        elif language in ["JavaScript", "TypeScript", "React", "React TypeScript"]:
            return self._parse_javascript(content, language)
        else:
            return self._parse_generic(content, language)
    
    def _parse_python(self, content: str) -> Dict:
        """Parse Python code using AST"""
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Calculate complexity (simplified - count control flow statements)
            complexity = sum(1 for node in ast.walk(tree) 
                           if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)))
            
            return {
                "language": "Python",
                "functions": functions,
                "classes": classes,
                "imports": list(set(imports)),
                "complexity": complexity,
                "lines_of_code": len(content.split('\n'))
            }
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error: {str(e)}")
            return self._parse_generic(content, "Python")
    
    def _parse_javascript(self, content: str, language: str) -> Dict:
        """Parse JavaScript/TypeScript code using regex patterns"""
        
        # Extract functions (function declarations and arrow functions)
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
        functions = re.findall(function_pattern, content)
        functions = [f[0] or f[1] for f in functions if f[0] or f[1]]
        
        # Extract classes
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        
        # Extract imports
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\)'
        imports = re.findall(import_pattern, content)
        imports = [i[0] or i[1] for i in imports if i[0] or i[1]]
        
        # Calculate complexity (count if, for, while, switch)
        complexity = (
            len(re.findall(r'\bif\s*\(', content)) +
            len(re.findall(r'\bfor\s*\(', content)) +
            len(re.findall(r'\bwhile\s*\(', content)) +
            len(re.findall(r'\bswitch\s*\(', content))
        )
        
        return {
            "language": language,
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "complexity": complexity,
            "lines_of_code": len(content.split('\n'))
        }
    
    def _parse_generic(self, content: str, language: str) -> Dict:
        """Generic parser for unsupported languages"""
        
        # Basic pattern matching
        functions = re.findall(r'(?:def|function|func|fn)\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        
        # Try to find import-like statements
        imports = re.findall(r'(?:import|include|require|use)\s+[\'"]?([^\s\'"]+)', content)
        
        return {
            "language": language,
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "complexity": 0,
            "lines_of_code": len(content.split('\n'))
        }
    
    def identify_frameworks(self, imports: List[str]) -> List[str]:
        """
        Identify frameworks from imports
        
        Args:
            imports: List of import statements
        
        Returns:
            List of identified frameworks
        """
        framework_patterns = {
            # Python
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'sqlalchemy': 'SQLAlchemy',
            'pandas': 'Pandas',
            'numpy': 'NumPy',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'scikit': 'Scikit-learn',
            
            # JavaScript/TypeScript
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'next': 'Next.js',
            'express': 'Express.js',
            'nestjs': 'NestJS',
            'svelte': 'Svelte',
            
            # Others
            'spring': 'Spring Framework',
            'laravel': 'Laravel',
            'rails': 'Ruby on Rails',
        }
        
        frameworks = set()
        imports_str = ' '.join(imports).lower()
        
        for pattern, framework in framework_patterns.items():
            if pattern in imports_str:
                frameworks.add(framework)
        
        return list(frameworks)
    
    def categorize_tech_stack(self, all_file_analysis: List[Dict]) -> Dict[str, List[str]]:
        """
        Categorize technology stack from all file analyses
        
        Args:
            all_file_analysis: List of file analysis results
        
        Returns:
            Dict with categorized tech stack
        """
        languages = set()
        frameworks = set()
        all_imports = []
        
        for analysis in all_file_analysis:
            if analysis.get('language') and analysis['language'] != 'Unknown':
                languages.add(analysis['language'])
            all_imports.extend(analysis.get('imports', []))
        
        # Identify frameworks
        frameworks = set(self.identify_frameworks(all_imports))
        
        # Identify databases
        databases = set()
        imports_str = ' '.join(all_imports).lower()
        db_keywords = {
            'mongodb': 'MongoDB',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'redis': 'Redis',
            'sqlite': 'SQLite',
            'cassandra': 'Cassandra',
            'dynamodb': 'DynamoDB',
        }
        
        for keyword, db_name in db_keywords.items():
            if keyword in imports_str:
                databases.add(db_name)
        
        return {
            "languages": sorted(list(languages)),
            "frameworks": sorted(list(frameworks)),
            "databases": sorted(list(databases)),
        }


# Global instance
parser_service = ParserService()
