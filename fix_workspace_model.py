#!/usr/bin/env python3
"""Fix the SlackWorkspace model to handle Slack's icon field properly."""

def fix_workspace_model():
    file_path = "src/slack_mcp/models/slack.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the icon field to accept Any type
    content = content.replace(
        'from typing import List, Optional, Dict, Any',
        'from typing import List, Optional, Dict, Any, Union'
    )
    
    content = content.replace(
        'icon: Optional[Dict[str, str]] = Field(default=None, description="Workspace icon URLs")',
        'icon: Optional[Dict[str, Any]] = Field(default=None, description="Workspace icon URLs")'
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed SlackWorkspace model to handle mixed icon types")

if __name__ == "__main__":
    fix_workspace_model()
