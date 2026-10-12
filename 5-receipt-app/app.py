# Q5: food receipt app
#   a. upload receipt image
#   b. extract it with vision model (gpt-6-luna can read images)
#   c. save to sqlite
#   d. user asks a question -> LLM calls tools that query the db -> answer

import base64
import json
import os
import sqlite3
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()                                  # reads .env file -> os.environ
client = OpenAI()                              # uses OPENAI_API_KEY from env
MODEL = os.getenv("MODEL", "gpt-6-luna")
DB = "data/receipts.db"

app = FastAPI()


# ---------------- database ----------------
def init_db():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY, store TEXT, date TEXT, total REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY, receipt_id INTEGER, name TEXT, price REAL)""")
    con.commit()
    con.close()


def query(sql, params=()):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, params).fetchall()
    con.close()
    return [dict(r) for r in rows]


init_db()


# ---------------- a. upload page ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()


# ---------------- b + c. extract and save ----------------
@app.post("/upload")
async def upload(file: UploadFile):
    image = base64.b64encode(await file.read()).decode()

    # ask the vision model to read the receipt and give back json
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": [
            {"type": "image_url",
             "image_url": {"url": f"data:{file.content_type};base64,{image}"}},
            {"type": "text", "text":
                "Read this food receipt. Reply with JSON only:\n"
                '{"store": "...", "date": "YYYY-MM-DD", "total": 0.0, '
                '"items": [{"name": "...", "price": 0.0}]}'},
        ]},
        ],
    )
    receipt = json.loads(response.choices[0].message.content)

    # save to db
    con = sqlite3.connect(DB)
    cur = con.execute("INSERT INTO receipts (store, date, total) VALUES (?, ?, ?)",
                      (receipt["store"], receipt["date"], receipt["total"]))
    receipt_id = cur.lastrowid
    for item in receipt["items"]:
        con.execute("INSERT INTO items (receipt_id, name, price) VALUES (?, ?, ?)",
                    (receipt_id, item["name"], item["price"]))
    con.commit()
    con.close()

    return receipt


# ---------------- d. AI tools ----------------
# these are the functions the LLM is allowed to call

def get_items(start_date, end_date):
    return query("""SELECT r.date, r.store, i.name, i.price
                    FROM items i JOIN receipts r ON r.id = i.receipt_id
                    WHERE r.date BETWEEN ? AND ?""", (start_date, end_date))


def get_total(start_date, end_date):
    rows = query("SELECT SUM(total) AS total FROM receipts WHERE date BETWEEN ? AND ?",
                 (start_date, end_date))
    return {"total": rows[0]["total"] or 0}


def find_item(name, start_date, end_date):
    return query("""SELECT r.date, r.store, i.name, i.price
                    FROM items i JOIN receipts r ON r.id = i.receipt_id
                    WHERE i.name LIKE ? AND r.date BETWEEN ? AND ?""",
                 ("%" + name + "%", start_date, end_date))


DATE_PARAMS = {"start_date": {"type": "string"}, "end_date": {"type": "string"}}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_items",
        "description": "list food items bought between two dates",
        "parameters": {"type": "object", "properties": DATE_PARAMS,
                       "required": ["start_date", "end_date"]}}},
    {"type": "function", "function": {
        "name": "get_total",
        "description": "total food expenses between two dates",
        "parameters": {"type": "object", "properties": DATE_PARAMS,
                       "required": ["start_date", "end_date"]}}},
    {"type": "function", "function": {
        "name": "find_item",
        "description": "find where (which store) an item was bought between two dates",
        "parameters": {"type": "object",
                       "properties": {"name": {"type": "string"}, **DATE_PARAMS},
                       "required": ["name", "start_date", "end_date"]}}},
]


def run_tool(name, args):
    if name == "get_items":
        return get_items(args["start_date"], args["end_date"])
    if name == "get_total":
        return get_total(args["start_date"], args["end_date"])
    if name == "find_item":
        return find_item(args["name"], args["start_date"], args["end_date"])


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(q: Question):
    messages = [
        {"role": "system", "content":
            f"Today is {date.today()}. You help the user with their food expenses. "
            "Always use the tools to get data, dates are YYYY-MM-DD."},
        {"role": "user", "content": q.question},
    ]

    # loop: model may call a tool, we run it, give the result back, until it answers
    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, reasoning_effort="none")
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return {"answer": msg.content}

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            output = run_tool(call.function.name, args)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(output)})
