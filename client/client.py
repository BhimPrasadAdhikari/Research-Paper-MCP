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

                print(result) # list of paper ids
                
    except Exception as e:
        print("Failed to connect", e)
        
if __name__ == "__main__":
    asyncio.run(main())