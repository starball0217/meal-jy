import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def ask_ai(prompt):
    message = client.messages.create(
        model="claude-haiku-5.5", max_tokens=10000,
        messages=[{"role": "user", "content" : prompt}]
    )
    answer = "".join(b.text for b in message.content if b. type == "text")
    return answer