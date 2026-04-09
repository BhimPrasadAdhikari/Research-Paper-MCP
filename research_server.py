import arxiv 
import json
import os
from typing import List 
from mcp.server.fastmcp import FastMCP 

PAPER_DIR = "papers"

mcp = FastMCP("research", port=8001)

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.

    Args:
        topic(str): The topic to search for
        max_results(int): Maximum number of results to retrieve (default: 5)
    
    Returns:
        List(str): list of paper IDs found in the search 
    """

    client = arxiv.Client()

    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)

    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "paper_info.json")

    try:
        with open(file_path, 'r') as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    paper_ids = []

    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
            "published": str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info

    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)
    
    return paper_ids 

if __name__ == "__main__":
    mcp.run(transport="sse")
