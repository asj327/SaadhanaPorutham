from fastapi import FastAPI
from pydantic import BaseModel
from firebase import db
from datetime import datetime
import uuid

app = FastAPI(title="saadhanaPorutham API")


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
    return {
        "message": "Welcome to SaadhanaPorutham ❤️"
    }


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