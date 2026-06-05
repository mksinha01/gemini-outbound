import os

files_to_update = [
    "ui/index.html",
    "server.py",
    "db.py",
    "agent.py",
    "app.yaml",
    "app.yaml.example",
    "start.sh",
    "render.yaml",
    "supabase_schema.sql"
]

for file_path in files_to_update:
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content.replace("gemini-3.1-flash-live-preview", "gemini-2.0-flash-exp")
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {file_path}")

import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv(".env")
sys.path.append(os.path.abspath("."))
from db import _sdb

async def update_db():
    try:
        client = _sdb()
        client.table("agent_profiles").update({"model": "gemini-2.0-flash-exp"}).eq("model", "gemini-3.1-flash-live-preview").execute()
        print("Updated agent_profiles in Supabase")
    except Exception as e:
        print(f"Error updating DB: {e}")

if __name__ == "__main__":
    asyncio.run(update_db())

