import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from confluent_kafka import Consumer
from supabase import create_client
from openai import AsyncOpenAI

load_dotenv()

# Kafka config
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "email-events")
consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    'security.protocol': os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
    'sasl.mechanisms': os.getenv("KAFKA_MECHANISM", "SCRAM-SHA-256"),
    'sasl.username': os.getenv("KAFKA_USERNAME"),
    'sasl.password': os.getenv("KAFKA_PASSWORD"),
    'group.id': "email-consumer-group",
    'auto.offset.reset': 'earliest'
})

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# OpenAI Client (new SDK)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def process_message(event):
    name = event.get("name")
    company = event.get("company")
    product_company = event.get("product_company")
    product_description = event.get("product_description")

    if not name or not company or not product_company or not product_description:
        print("[Warning] Missing fields in event")
        return

    try:
        # Research
        research_resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Give 3–4 recent, impactful, and relevant facts about {company} that could be useful for a personalized B2B cold email. Use bullet points."
            }]
        )
        research_summary = research_resp.choices[0].message.content.strip()

        # Email
        email_prompt = f"""
You are writing a personalized cold outbound email to {name} at {company}.
Use the following research to inform the email:
{research_summary}

You're reaching out from {product_company}. Here is the product description:
{product_description}

Keep the email short, compelling, and confident. Do not include a sign-off or sender name — just end the message naturally.
"""
        email_resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": email_prompt.strip()}]
        )
        generated_email = email_resp.choices[0].message.content.strip()

        # Save to Supabase
        supabase.table("email_interactions").insert({
            "name": name,
            "company": company,
            "product_company": product_company,
            "product_description": product_description,
            "research_summary": research_summary,
            "generated_email": generated_email,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        print(f"[✅ Success] Inserted email for {name} at {company}")

    except Exception as e:
        print(f"[❌ Error] {str(e)}")

async def consume():
    consumer.subscribe([TOPIC_NAME])
    print(f"Subscribed to topic: {TOPIC_NAME}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error:", msg.error())
                continue

            event = json.loads(msg.value().decode('utf-8'))
            print(f"[Kafka] Message: {event}")
            await process_message(event)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(consume())
