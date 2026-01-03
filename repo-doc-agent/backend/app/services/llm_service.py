from typing import List, Dict, Optional
from groq import Groq
from app.core.config import settings
from app.core.logger import logger


class LLMService:
    """Service for LLM operations using Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Fast and capable (updated from deprecated 3.1)
        self.max_tokens = 2048
    
    def _create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        Create chat completion with Groq
        
        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature
        
        Returns:
            Response content
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise Exception(f"LLM API error: {str(e)}")
    
    def summarize_code(self, code: str, language: str, file_path: str) -> str:
        """
        Generate a summary of code file
        
        Args:
            code: Source code content
            language: Programming language
            file_path: File path for context
        
        Returns:
            Plain English summary
        """
        prompt = f"""Analyze this {language} code file and provide a clear, concise summary.

File: {file_path}

Code:
```{language}
{code[:3000]}
```

Instructions:
1. First, identify the PRIMARY purpose of this file (what problem does it solve?)
2. Then, list the MAIN functionality it provides
3. Finally, note any important patterns, frameworks, or architectural decisions

Write a 2-3 sentence summary that focuses on WHAT the code does and WHY it exists, not HOW it works.
Avoid generic statements. Be specific about this particular file's role in the project."""

        messages = [
            {"role": "system", "content": "You are an expert software architect who understands code at a high level. You explain code purpose clearly and concisely, focusing on business value and architectural decisions."},
            {"role": "user", "content": prompt}
        ]
        
        return self._create_chat_completion(messages)
    
    def extract_features_from_analysis(self, code_analysis: Dict) -> List[str]:
        """
        Extract product features from code analysis
        
        Args:
            code_analysis: Dict containing code analysis results
        
        Returns:
            List of feature descriptions
        """
        prompt = f"""You are analyzing a software product to identify its key features for a product page.

Code Analysis Data:
{str(code_analysis)[:2000]}

Task: Extract 5-7 product features that would matter to end users or business stakeholders.

Guidelines:
1. Focus on USER-FACING capabilities, not implementation details
2. Each feature should answer: "What can users DO with this?"
3. Use benefit-driven language (e.g., "Automate email follow-ups" not "Has email service")
4. Avoid technical jargon - write for non-technical stakeholders
5. Be specific about the actual functionality, not generic capabilities

Example good features:
- "Track and manage customer leads in a centralized dashboard"
- "Automatically send personalized follow-up emails based on user behavior"
- "Generate detailed analytics reports with customizable metrics"

Example bad features:
- "Uses React for the frontend" (implementation detail)
- "Has a database" (too generic)
- "Scalable architecture" (vague)

Format: Return ONLY a list with each feature on a new line starting with "- "
Focus on what makes THIS product unique and valuable."""

        messages = [
            {"role": "system", "content": "You are a product manager with expertise in translating technical capabilities into clear, compelling product features. You understand what matters to users and stakeholders."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._create_chat_completion(messages, temperature=0.5)
        
        # Parse response into list
        features = [line.strip().lstrip('- ') for line in response.split('\n') if line.strip().startswith('-')]
        
        return features
    
    def generate_executive_summary(self, repo_info: Dict) -> str:
        """
        Generate executive summary for marketing
        
        Args:
            repo_info: Dict with repository information
        
        Returns:
            Executive summary paragraph
        """
        prompt = f"""Create a compelling executive summary for this software product.

Product Information:
- Name: {repo_info.get('name', 'Unknown')}
- Description: {repo_info.get('description', 'N/A')}
- Tech Stack: {', '.join(repo_info.get('tech_stack', {}).get('languages', []))}
- Key Features: {', '.join(repo_info.get('features', [])[:5])}

Instructions:
Write a 3-4 sentence executive summary following this structure:

1. Opening: What is this product and what problem does it solve?
2. Value Proposition: What makes it valuable? What benefits does it provide?
3. Technology: Briefly mention the tech stack (only if relevant to the value prop)
4. Impact: What outcomes can users/businesses expect?

Guidelines:
- Write for C-level executives and business decision-makers
- Focus on BUSINESS VALUE and OUTCOMES, not technical features
- Be specific about what THIS product does (avoid generic statements)
- Use clear, professional language
- Avoid buzzwords and marketing fluff
- Don't mention "our product" or "we" - write in third person

Example structure:
"[Product Name] is a [type] that [solves X problem] by [doing Y]. It enables [users/businesses] to [achieve outcome], resulting in [benefit]. Built with [tech if relevant], the platform [key differentiator]. Organizations using [Product Name] can expect [specific outcome/metric]."

Write the executive summary now:"""

        messages = [
            {"role": "system", "content": "You are a senior product marketing strategist who writes compelling, clear executive summaries. You understand how to communicate technical products to business audiences."},
            {"role": "user", "content": prompt}
        ]
        
        return self._create_chat_completion(messages, temperature=0.6)
    
    def generate_use_cases(self, features: List[str], tech_stack: Dict) -> List[str]:
        """
        Generate use cases based on features
        
        Args:
            features: List of product features
            tech_stack: Technology stack information
        
        Returns:
            List of use case descriptions
        """
        prompt = f"""Generate 4-5 realistic, specific use cases for this software product.

Product Features:
{chr(10).join(f'- {f}' for f in features)}

Tech Stack: {', '.join(tech_stack.get('languages', []))}

Instructions:
For each use case, describe a SPECIFIC scenario where this product solves a real problem.

Format for each use case:
"[User/Company Type]: [Specific scenario and problem] → [How product solves it] → [Measurable outcome]"

Guidelines:
1. Be SPECIFIC - name actual user types, industries, or scenarios
2. Focus on PROBLEMS being solved, not just features being used
3. Include MEASURABLE outcomes or benefits
4. Make it realistic and relatable
5. Each use case should be 2-3 sentences max

Example good use cases:
- "E-commerce Startup: A growing online store struggles to follow up with abandoned cart customers manually. Using automated email sequences, they recover 15% of abandoned carts and increase monthly revenue by $50K."
- "Sales Team at SaaS Company: Sales reps spend 3 hours daily manually updating CRM and sending follow-ups. The automated lead tracking and email system saves 15 hours per week per rep, allowing them to focus on closing deals."

Example bad use cases:
- "Businesses can use this to manage data" (too vague)
- "Users can create dashboards" (just describing a feature)

Return ONLY a list with each use case on a new line starting with "- "
Make each use case tell a mini-story of transformation."""

        messages = [
            {"role": "system", "content": "You are a solutions consultant who understands how software solves real business problems. You create compelling, specific use cases that resonate with potential customers."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._create_chat_completion(messages, temperature=0.5)
        
        use_cases = [line.strip().lstrip('- ') for line in response.split('\n') if line.strip().startswith('-')]
        
        return use_cases
    
    def generate_marketing_points(self, repo_info: Dict) -> List[str]:
        """
        Generate marketing talking points
        
        Args:
            repo_info: Complete repository information
        
        Returns:
            List of marketing talking points
        """
        prompt = f"""Create 5-6 compelling marketing talking points for this product.

Product Information:
- Name: {repo_info.get('name', 'Unknown')}
- Features: {', '.join(repo_info.get('features', []))}
- Tech Stack: {str(repo_info.get('tech_stack', {}))}

Instructions:
Each talking point should be a single, punchy sentence that highlights a unique selling point.

Format: [Benefit/Outcome] + [How/Why it matters]

Guidelines:
1. Lead with the BENEFIT or OUTCOME, not the feature
2. Be SPECIFIC - use numbers, comparisons, or concrete examples when possible
3. Focus on competitive advantages or unique capabilities
4. Avoid generic claims ("best", "powerful", "innovative")
5. Make it conversational and persuasive
6. Each point should stand alone as a compelling reason to use the product

Example good talking points:
- "Automate 80% of your lead follow-up process, freeing your sales team to focus on closing deals instead of manual outreach."
- "Get your first campaign running in under 10 minutes with pre-built templates and intuitive drag-and-drop design."
- "Track every customer interaction in one place, eliminating the need to juggle between 5 different tools."

Example bad talking points:
- "Built with modern technology" (vague, not a benefit)
- "Easy to use interface" (generic, everyone claims this)
- "Scalable and reliable" (not specific or differentiated)

Return ONLY a list with each talking point on a new line starting with "- "
Make each point something a salesperson would actually say to a prospect."""

        messages = [
            {"role": "system", "content": "You are a top-performing sales professional who knows how to communicate product value clearly and persuasively. You focus on outcomes and benefits that resonate with buyers."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._create_chat_completion(messages, temperature=0.6)
        
        points = [line.strip().lstrip('- ') for line in response.split('\n') if line.strip().startswith('-')]
        
        return points
    
    def identify_integrations(self, code_analysis: Dict) -> List[str]:
        """
        Identify third-party integrations from code
        
        Args:
            code_analysis: Code analysis with imports/dependencies
        
        Returns:
            List of integration names
        """
        # Extract imports and dependencies
        imports = []
        for file_analysis in code_analysis.get('files', []):
            imports.extend(file_analysis.get('imports', []))
        
        # Common integration patterns
        integration_keywords = {
            'stripe': 'Stripe Payment Processing',
            'paypal': 'PayPal Integration',
            'aws': 'Amazon Web Services (AWS)',
            'azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform',
            'firebase': 'Firebase',
            'mongodb': 'MongoDB Database',
            'postgresql': 'PostgreSQL Database',
            'redis': 'Redis Cache',
            'elasticsearch': 'Elasticsearch',
            'sendgrid': 'SendGrid Email',
            'twilio': 'Twilio Communications',
            'slack': 'Slack Integration',
            'github': 'GitHub Integration',
            'gitlab': 'GitLab Integration',
            'docker': 'Docker Containerization',
            'kubernetes': 'Kubernetes Orchestration',
            'oauth': 'OAuth Authentication',
            'jwt': 'JWT Authentication',
            'graphql': 'GraphQL API',
            'rest': 'REST API',
            'websocket': 'WebSocket Real-time',
        }
        
        integrations = set()
        imports_str = ' '.join(imports).lower()
        
        for keyword, integration_name in integration_keywords.items():
            if keyword in imports_str:
                integrations.add(integration_name)
        
        return list(integrations)


# Global instance
llm_service = LLMService()
