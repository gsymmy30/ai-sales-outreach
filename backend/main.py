from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from confluent_kafka import Producer
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TOPIC_NAME = os.getenv("KAFKA_TOPIC", "email-events")

producer = Producer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    'security.protocol': os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
    'sasl.mechanisms': os.getenv("KAFKA_MECHANISM", "SCRAM-SHA-256"),
    'sasl.username': os.getenv("KAFKA_USERNAME"),
    'sasl.password': os.getenv("KAFKA_PASSWORD"),
})

@app.post("/enqueue")
async def enqueue_email_job(request: Request):
    body = await request.json()
    name = body.get("name")
    company = body.get("company")
    product_company = body.get("product_company")
    product_description = body.get("product_description")

    if not name or not company or not product_company or not product_description:
        return {"error": "Missing one or more required fields."}

    event = {
        "name": name,
        "company": company,
        "product_company": product_company,
        "product_description": product_description
    }

    try:
        producer.produce(
            topic=TOPIC_NAME,
            value=json.dumps(event).encode("utf-8")
        )
        producer.flush()
        return {"status": "Message enqueued successfully."}
    except Exception as e:
        return {"error": str(e)}
