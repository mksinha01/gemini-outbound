import asyncio
import os
import sys
sys.path.append(os.path.abspath("."))
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv(".env")
from livekit import agents
import agent as ag

async def main():
    print("Testing session build with tools...")
    try:
        def my_dummy_tool(x: str) -> str:
            """A dummy tool."""
            return x
        
        session = ag._build_session([my_dummy_tool], "Hello")
        print("Session built successfully:", session)
    except Exception as e:
        print("Error building session:", e)

if __name__ == "__main__":
    asyncio.run(main())
