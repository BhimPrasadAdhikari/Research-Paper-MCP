import arxiv 
import json
import typing import List 
from mcp.server.fastmcp import FastMCP 

PAPER_DIR = "papers"

mcp = FastMCP("research", port=8001)
