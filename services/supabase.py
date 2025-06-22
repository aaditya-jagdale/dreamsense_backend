from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

class Supabase:
    def __init__(self):
        self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    def get_prompt(self):
        response = self.client.table("daily_read").select("*").eq("title", "PROMPT").execute()