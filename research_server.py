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

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper accross all topic directories

    Args:
        paper_id: id of paper
    """

    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "paper_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)

                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print("error")
                    continue 
    return f"There's no saved information related to paper {paper_id}"

@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory
    """
    folders = []

    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)

            if os.path.isdir(topic_path):
                paper_file = os.path.join(topic_path, "paper_info.json")

                if os.path.isfile(paper_file):
                    folders.append(topic_dir) 
    
    # create a simple MD list 
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found\n"
    
    return content

@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "paper_info.json")

    if not os.path.exists(papers_file):
        return f"No papers found for specified topic."
    try:
        with open(papers_file, 'r') as json_file:
            papers_data = json.load(json_file)
        
        content = f"Papers on {topic.replace('_', ' ').title()}"
        content += f"Total papers: {len(papers_data)}"

        for paper_id, paper_info in papers_data.items():
            content += f"{paper_info['title']}\n"
            content += f"Paper Id: {paper_id}\n"
            content += f"Authors: {', '.join(paper_info.get('authors', []))}\n"
            content += f"Published: {paper_info['published']}\n"
            content += f"PDF URL: [{paper_info['pdf_url']}]\n\n"

            content += f"### Summary\n"
            content += f"{paper_info['summary'][:500]}...\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"Error reading papers data for {topic}. The paper data file is corrupted."


if __name__ == "__main__":
    mcp.run(transport="sse")
