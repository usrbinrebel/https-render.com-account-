from flask import Flask, request
import requests
import os
from datetime import datetime
import random

app = Flask(__name__)

# Get environment variables
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DB_ID = os.environ.get("NOTION_DB_ID")

def save_to_notion(question, answer):
    notion_url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Question": {"title": [{"text": {"content": question}}]},
            "Answer": {"rich_text": [{"text": {"content": answer}}]},
            "Timestamp": {"date": {"start": datetime.now().isoformat()}},
            "Glitch": {"select": {"name": "🌪️"}}
        }
    }
    res = requests.post(notion_url, headers=headers, json=data)
    print("Notion status:", res.status_code)

@app.route('/ask', methods=['POST'])
def ask_question():
    user_question = request.form.get("question")
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B",
            headers=headers,
            json={"inputs": user_question}
        )
        ai_answer = response.json()[0]['generated_text'] if response.status_code == 200 else "⚠️ Toaster malfunction."
    except Exception as e:
        ai_answer = f"🔥 SYSTEM ERROR: {str(e)}"

    save_to_notion(user_question, ai_answer)
    return f"🎱 {ai_answer}"

@app.route('/8ball')
def eight_ball():
    answers = [
        "Signs point to 'ingermop'.",
        "Grandma says yes, but only under a waxing moon.",
        "404: Future unclear.",
        "Ask again after rebooting reality.",
        "Absolutely. Or absolutely not.",
        "You already know the answer."
    ]
    return f"🎱 {random.choice(answers)}"

if __name__ == '__main__':
    app.run()
