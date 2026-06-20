import os
import random
import string
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="URL Shortener")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "url-shortener")

def get_table():
    return dynamodb.Table(TABLE_NAME)

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

class ShortenRequest(BaseModel):
    url: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/shorten")
def shorten_url(request: ShortenRequest):
    code = generate_code()
    table = get_table()
    table.put_item(Item={
        "code": code,
        "url": request.url,
        "clicks": 0
    })
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    return {"short_url": f"{base_url}/{code}", "code": code}

@app.get("/stats/{code}")
def get_stats(code: str):
    table = get_table()
    response = table.get_item(Key={"code": code})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"code": code, "url": item["url"], "clicks": item["clicks"]}

@app.get("/{code}")
def redirect_url(code: str):
    table = get_table()
    response = table.get_item(Key={"code": code})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="URL not found")
    table.update_item(
        Key={"code": code},
        UpdateExpression="SET clicks = clicks + :inc",
        ExpressionAttributeValues={":inc": 1}
    )
    return RedirectResponse(url=item["url"])

@app.get("/version")
def version():
    return {"version": "1.0.0", "service": "url-shortener"}