import asyncio 
from mcp.client.session import ClientSession 
from mcp.client.sse import sse_client 

MCP_SERVER_URL = "http://localhost:8001/sse"

async def main():
    print("Connecting....")
    try:
        async with sse_client(MCP_SERVER_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Connected")

                tools_response = await session.list_tools()

                for tool in tools_response.tools:
                    print(f"Tool found: {tool.name}")
                    print(f"Description: {tool.description}")
                
                # test the search_papers tool offered by the MCP server "research"
                result = await session.call_tool(
                    "search_papers",
                    {"topic": "vision language model", "max_results": 2}
                )

                # test the extract_info tool 

                # The MCP tool returns a list of items as multiple TextContent objects
                paper_ids = [content.text for content in result.content if content.type == "text"]

                print("\nextract info tool response: ")

                for paper_id in paper_ids:
                    print(f"Extracting info for {paper_id}...")
                    paper_info = await session.call_tool(
                        "extract_info",
                        {"paper_id": paper_id}
                    )
                    
                    # Print the title/content just to make it readable
                    print(paper_info.content[0].text)
                    print("-" * 50)

                # checking get_topic_papers

                resources_resp = await session.list_resources()
                print("\nResources offerd by server:")
                for res in resources_resp.resources:
                    print(f"- {res.name} | uri={res.uri} | desc={res.description}")
                
                # trying to read the "papers://folders" resource
                uri = "papers://folders"
                print(f"\nReading resource {uri} ...")
                try:
                    read_res = await session.read_resource(uri)
                    for item in read_res.contents:
                        text = getattr(item, "text", None)
                        if text is not None:
                            print("\n Resource Text ")
                            print(text)
                except Exception as e:
                    print("Failed to read resource:", e)
                
                # list available resource templates (dynamic resources):
                templates_resp = await session.list_resource_templates()
                print("Resource Templates offered by server: ")
                for tmpl in templates_resp.resourceTemplates:
                    print(f"{tmpl} | uriTemplate: {tmpl.uriTemplate} | desc={tmpl.description}")

                topic = "vision language model"
                uri = f"papers://{topic.replace(' ', '_')}"

                try:
                    read_res = await session.read_resource(uri)
                    for item in read_res.contents:
                        text = getattr(item, "text", None)
                        if text is not None:
                            print("Resource Text")
                            print(text) 
                except Exception as e:
                    print("Failed to read resource: ", e)




                
    except Exception as e:
        print("Failed to connect:", e)
        
if __name__ == "__main__":
    asyncio.run(main())