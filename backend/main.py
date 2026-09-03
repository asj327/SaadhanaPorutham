from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase import db
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="saadhanaPorutham API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ObjectProfile(BaseModel):
    name: str
    type: str
    bio: str
    personality: str
    attachment_style: str
    love_language: str
    turn_ons: str
    turn_offs: str
    green_flags: str
    red_flags: str


@app.get("/")
def home():
    return {"message": "Welcome to saadhanaPorutham ??"}


@app.post("/objects")
def create_object(obj: ObjectProfile):
    object_id = str(uuid.uuid4())

    object_data = {
        "id": object_id,
        "name": obj.name,
        "type": obj.type,
        "bio": obj.bio,
        "personality": obj.personality,
        "attachment_style": obj.attachment_style,
        "love_language": obj.love_language,
        "turn_ons": obj.turn_ons,
        "turn_offs": obj.turn_offs,
        "green_flags": obj.green_flags,
        "red_flags": obj.red_flags,
        "created_at": datetime.now().isoformat()
    }

    db.collection("objects").document(object_id).set(object_data)

    return {
        "status": "success",
        "object": object_data
    }


@app.get("/objects")
def get_objects():
    objects = []

    docs = db.collection("objects").stream()

    for doc in docs:
        objects.append(doc.to_dict())

    return {
        "status": "success",
        "objects": objects
    }

@app.post("/objects/generate")
def generate_object(object_type: str):

    prompt = f"""
Create a funny dating profile for this everyday object:

{object_type}

The app is called saadhanaPorutham, where everyday objects date each other.

Treat the object like a dating-app user.

Return ONLY ONE valid JSON object.

The JSON MUST have exactly these fields:

name
type
bio
personality
attachment_style
love_language
turn_ons
turn_offs
green_flags
red_flags

Make everything specific to {object_type}.
Use its physical properties, purpose and common problems.
Be funny, creative and slightly dramatic.
Keep each value short.

Do not use markdown.
Do not use ```json.
Do not add explanations.
"""

    try:

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You create funny dating profiles for everyday objects."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=600
        )

        profile_text = response.choices[0].message.content.strip()

        # Remove markdown if the model adds it
        if profile_text.startswith("```json"):
            profile_text = profile_text[7:]

        if profile_text.startswith("```"):
            profile_text = profile_text[3:]

        if profile_text.endswith("```"):
            profile_text = profile_text[:-3]

        profile_text = profile_text.strip()

        import json

        profile = json.loads(profile_text)

        # Save profile to Firestore
        doc_ref = db.collection("objects").add(profile)

        object_id = doc_ref[1].id

        return {
            "status": "success",
            "object_id": object_id,
            "profile": json.dumps(profile)
        }

    except Exception as e:

        print("Groq/Firestore error:", e)

        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/objects/{object_id}/like")
def like_object(object_id: str):

    print("LIKE RECEIVED:", object_id)

    try:
        doc_ref = db.collection("likes").add({
            "object_id": object_id,
            "action": "like"
        })

        print("FIRESTORE DOCUMENT CREATED:", doc_ref[1].id)

        return {
            "status": "success",
            "message": "Object liked",
            "document_id": doc_ref[1].id
        }

    except Exception as e:
        print("FIRESTORE ERROR:", repr(e))
        raise

@app.post("/objects/{object_id}/pass")
def pass_object(object_id: str):

    print("PASS RECEIVED:", object_id)

    try:
        doc_ref = db.collection("likes").add({
            "object_id": object_id,
            "action": "pass"
        })

        print("FIRESTORE DOCUMENT CREATED:", doc_ref[1].id)

        return {
            "status": "success",
            "message": "Object passed",
            "document_id": doc_ref[1].id
        }

    except Exception as e:
        print("FIRESTORE ERROR:", repr(e))
        raise