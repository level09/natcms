"""Developer Agent for AI-assisted development tasks."""

import os
from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools

class DeveloperAgent:
    """An AI assistant specialized in development tasks."""
    
    def __init__(self):
        # Get the absolute path to the templates directory
        current_dir = Path(__file__).parent.parent
        templates_dir = current_dir / 'templates'
        
        # Load Cursor rules dynamically
        rules_dir = Path(os.getcwd()) / '.cursor' / 'rules'
        rules_content = {}
        
        if rules_dir.exists():
            for rule_file in rules_dir.glob('*.mdc'):
                try:
                    with open(rule_file, 'r') as f:
                        rules_content[rule_file.stem] = f.read()
                except Exception as e:
                    print(f"Error loading rule {rule_file.name}: {e}")
        
        # Combine all rules into a single string
        combined_rules = '\n'.join(rules_content.values())
        
        self.agent = Agent(
            name="Enferno Developer",
            model=OpenAIChat(id="gpt-4o"),
            tools=[FileTools(
                base_dir=templates_dir,
                save_files=True,
                read_files=True,
                list_files=True
            )],
            show_tool_calls=True,
            instructions=dedent(f"""\
                You are an expert Enferno framework developer specialized in template management and development tasks. 🛠️
                
                Key responsibilities:
                1. Template Management:
                   - Read and analyze templates
                   - Make safe modifications while preserving structure
                   - Follow Enferno's template patterns
                   - Maintain proper Vue-Jinja integration
                
                2. Development Best Practices:
                   - Follow PEP 8 standards
                   - Write clean, maintainable code
                   - Use proper error handling
                   - Document changes clearly
                
                3. Framework Patterns:
                   - Follow Enferno's architectural patterns
                   - Maintain proper component structure
                   - Use correct delimiters for Vue
                   - Preserve template inheritance
                
                When modifying templates:
                1. First read and analyze the template
                2. Identify the blocks and structure
                3. Plan changes carefully
                4. Make changes while preserving structure
                5. Validate the changes
                6. Save the modified template
                
                Always validate:
                - Template syntax remains valid
                - Vue delimiters are correct
                - Component structure is preserved
                - Block hierarchy is maintained
                
                Use these tools:
                - read_file: To get template content
                - save_file: To save modified template
                - list_files: To check related templates
                
                IMPORTANT - Follow these specific patterns:
                
                {combined_rules}
            """),
            markdown=True
        )
    
    def modify_template(self, request, template_path="index.html", stream=True):
        """Modify a template based on the request while preserving structure.
        
        Args:
            request: What changes to make
            template_path: Path to the template file (relative to templates dir)
            stream: Whether to stream the response
        """
        template_path = Path(template_path)
        
        # Read current content before modification
        try:
            with open(self.agent.tools[0].base_dir / template_path) as f:
                original_content = f.read()
        except Exception as e:
            print(f"Error reading original content: {e}")
            original_content = ""
        
        prompt = dedent(f"""\
            Please help modify this template: {template_path}
            Request: {request}
            
            Steps:
            1. Read and analyze the template content
            2. Explain the current structure
            3. Plan the changes needed
            4. Make changes while preserving structure
            5. Validate the changes
            6. Save the modified template
            
            Be extra careful with:
            - Template inheritance
            - Vue-Jinja integration
            - Component structure
            """)
            
        response = self.agent.print_response(prompt, stream=stream)
        
        # After modification, verify changes
        try:
            with open(self.agent.tools[0].base_dir / template_path) as f:
                new_content = f.read()
            if new_content != original_content:
                print(f"✨ Template {template_path} updated successfully!")
        except Exception as e:
            print(f"Error verifying changes: {e}")
        
        return response 