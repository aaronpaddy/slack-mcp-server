#!/usr/bin/env python3
"""Quick fix for server.py to add nextCursor=None"""

import os

def fix_server():
    server_path = "src/slack_mcp/server.py"
    
    # Read the file
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Fix the list_resources handler
    content = content.replace(
        "return ListResourcesResult(resources=resources)",
        "return ListResourcesResult(resources=resources, nextCursor=None)"
    )
    
    content = content.replace(
        "return ListResourcesResult(resources=[])",
        "return ListResourcesResult(resources=[], nextCursor=None)"
    )
    
    # Fix the list_tools handler
    content = content.replace(
        "return ListToolsResult(tools=tools)",
        "return ListToolsResult(tools=tools, nextCursor=None)"
    )
    
    content = content.replace(
        "return ListToolsResult(tools=[])",
        "return ListToolsResult(tools=[], nextCursor=None)"
    )
    
    # Write the file back
    with open(server_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed server.py - added nextCursor=None to MCP responses")

if __name__ == "__main__":
    fix_server()
