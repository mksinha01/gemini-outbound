import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv(".env")
sys.path.append(os.path.abspath("."))
from db import get_logs
import json
import json

async def main():
    logs = await get_logs(limit=20)
    for log in logs:
        print(f"[{log.get('level')}] {log.get('source')}: {log.get('message')} - {log.get('details')}")

if __name__ == "__main__":
    asyncio.run(main())
