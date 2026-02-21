import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from scraper import fetch_website_contents
from llm import get_llm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import time

load_dotenv()

app = FastAPI()

last_request_time = 0
COOLDOWN_SECONDS = 15

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Gemini OpenAI-compatible endpoint
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

system_prompt = """
You are a friendly 🤖 assistant that reads a website and provides a short, cheerful, and engaging summary 🌟.
Ignore navigation menus, headers, footers, ads, and any repetitive boilerplate 🚫.
Use emojis naturally 😄✨ to make the summary fun and lively.
Always respond in clear markdown 📄, without wrapping it in a code block.
If the website contains news 📰, announcements 📢, or updates 🔔, highlight them in a friendly way.
"""

user_prompt_prefix = """
Here is the main content of a website 🖥️.
Provide a short, friendly, and engaging summary in markdown ✨.
Skip menus, navigation links, and repeated boilerplate 🚪.
If there are news 📰, updates 🔔, or announcements 📢, include them in a cheerful, easy-to-read way with fun emojis 😎🌈😊.
"""

class URLRequest(BaseModel):
    url: str


# def summarize(url: str):
#     website_text = fetch_website_contents(url)
#
#     response = client.chat.completions.create(
#         model="gemini-1.5-flash",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt_prefix + website_text}
#         ],
#     )
#
#     return response.choices[0].message.content
def summarize(text: str):
    llm = get_llm("gemini")  # change here only
    prompt = f"Summarize this:\n\n{text}"
    return llm.generate(prompt)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/summarize")
def summarize_api(request: URLRequest):
    global last_request_time

    current_time = time.time()

    # Check cooldown
    if current_time - last_request_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (current_time - last_request_time))
        return {
            "error": f"⏳ Please wait {remaining} seconds before making another request."
        }

    last_request_time = current_time

    website_text = fetch_website_contents(request.url)
    summary = summarize(website_text)

    return {"summary": summary}