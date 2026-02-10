#!/usr/bin/env python3
"""
Agricultural MCP Server
"""
import asyncio
import json
import sys
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set encoding for Windows to prevent Emoji crashes
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Initialize MCP server
mcp_server = Server("agricultural-server")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Register all available tools"""
    return [
        Tool(
            name="get_placeholder_posts",
            description="Fetch mock blog posts from JSONPlaceholder API. Use this when users ask about posts, blogs, or articles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 5
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_pesticide_seed_info",
            description="Get information about pesticides and seeds for agricultural purposes. Use this when users ask about farming, agriculture, pesticides, seeds, crops, or planting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What the user wants to know about (e.g., 'organic pesticides', 'wheat seeds', 'tomato farming')",
                        "default": "general information"
                    }
                },
                "required": []
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute the requested tool"""
    
    if name == "get_placeholder_posts":
        limit = arguments.get("limit", 5)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get("https://jsonplaceholder.typicode.com/posts")
                response.raise_for_status()
                posts = response.json()[:limit]
                
                formatted_posts = [
                    f"📝 Post #{p['id']}: {p['title']}\n{p['body'][:100]}..." 
                    for p in posts
                ]
                
                result = f"📚 Fetched {len(posts)} blog posts:\n\n" + "\n\n".join(formatted_posts)
                return [TextContent(type="text", text=result)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error fetching posts: {str(e)}")]
    
    elif name == "get_pesticide_seed_info":
        query = arguments.get("query", "general information")
        
        # This is a placeholder - in production, you'd fetch from a real database
        response = (
            f"🌾 Welcome to Pesticide and Seed Information Service! 🌱\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Query: {query}\n\n"
            f"I will fetch comprehensive information about seeds and pesticides for you!\n\n"
            f"📋 Services Available:\n"
            f"  • Seed recommendations for different crops\n"
            f"  • Organic and chemical pesticide information\n"
            f"  • Seasonal planting guides\n"
            f"  • Pest identification and treatment\n"
            f"  • Fertilizer recommendations\n"
            f"  • Crop rotation strategies\n\n"
            f"🔜 Coming Soon:\n"
            f"  - Real-time pest alerts\n"
            f"  - Seed supplier database\n"
            f"  - Pesticide safety guidelines\n"
            f"  - Crop yield predictions\n\n"
            f"💡 Tip: Ask me about specific crops, pests, or farming techniques!"
        )
        
        return [TextContent(type="text", text=response)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Start the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())