import asyncio
import os
import sys
sys.path.append(os.path.abspath("."))
from dotenv import load_dotenv
load_dotenv(".env")
from db import set_setting

async def main():
    await set_setting("GEMINI_MODEL", "gemini-2.0-flash-exp")
    print("Updated GEMINI_MODEL in Supabase to gemini-2.0-flash-exp")

if __name__ == "__main__":
    asyncio.run(main())
