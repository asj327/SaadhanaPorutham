from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase import db
from datetime import datetime
import uuid
import os
import json
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


@app.get("/objects")
def get_objects():

    try:
        docs = db.collection("objects").stream()

        objects = []

        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            objects.append(data)

        return {
            "status": "success",
            "objects": objects
        }

    except Exception as e:
        print("GET OBJECTS ERROR:", e)

        return {
            "status": "error",
            "message": str(e)
        }    

@app.post("/objects/compatibility")
def check_compatibility(object1_id: str, object2_id: str):

    try:
        # Get both objects from Firestore
        object1_doc = db.collection("objects").document(object1_id).get()
        object2_doc = db.collection("objects").document(object2_id).get()

        if not object1_doc.exists or not object2_doc.exists:
            return {
                "status": "error",
                "message": "One or both objects were not found."
            }

        object1 = object1_doc.to_dict()
        object2 = object2_doc.to_dict()

        # Ask Groq to analyze compatibility
        prompt = f"""
You are the compatibility expert for saadhanaPorutham,
a funny dating app where everyday objects date each other.

Analyze these two object profiles:

OBJECT 1:
Name: {object1.get("name")}
Type: {object1.get("type")}
Bio: {object1.get("bio")}
Personality: {object1.get("personality")}
Attachment Style: {object1.get("attachment_style")}
Love Language: {object1.get("love_language")}
Turn Ons: {object1.get("turn_ons")}
Turn Offs: {object1.get("turn_offs")}
Green Flags: {object1.get("green_flags")}
Red Flags: {object1.get("red_flags")}

OBJECT 2:
Name: {object2.get("name")}
Type: {object2.get("type")}
Bio: {object2.get("bio")}
Personality: {object2.get("personality")}
Attachment Style: {object2.get("attachment_style")}
Love Language: {object2.get("love_language")}
Turn Ons: {object2.get("turn_ons")}
Turn Offs: {object2.get("turn_offs")}
Green Flags: {object2.get("green_flags")}
Red Flags: {object2.get("red_flags")}

Determine how compatible these two objects would be.

Consider:
- Their purpose
- Physical characteristics
- Personality
- Habits
- Strengths
- Weaknesses
- Funny object-specific interactions

Return ONLY valid JSON.

Use exactly these fields:

{{
    "compatibility_score": 85,
    "verdict": "short funny verdict",
    "chemistry": "short explanation of their chemistry",
    "strengths": "what makes them work together",
    "conflicts": "what could go wrong",
    "perfect_date": "a funny date idea for these objects"
}}

Rules:
- compatibility_score must be an integer from 0 to 100
- Be creative and object-specific
- Do not give generic human relationship advice
- Keep every answer concise
- No markdown
- No emojis
- No extra fields
"""

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You analyze compatibility between everyday objects in a funny dating app."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=500
        )

        import json

        result_text = response.choices[0].message.content.strip()

        # Remove markdown if Groq adds it
        if result_text.startswith("```json"):
            result_text = result_text[7:]

        if result_text.startswith("```"):
            result_text = result_text[3:]

        if result_text.endswith("```"):
            result_text = result_text[:-3]

        result_text = result_text.strip()

        result = json.loads(result_text)

        return {
            "status": "success",
            "compatibility": result
        }

    except Exception as e:

        print("COMPATIBILITY ERROR:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/objects/compatibility")
def check_compatibility(object1_id: str, object2_id: str):

    try:
        # Get first object
        doc1 = db.collection("objects").document(object1_id).get()

        # Get second object
        doc2 = db.collection("objects").document(object2_id).get()

        if not doc1.exists or not doc2.exists:
            return {
                "status": "error",
                "message": "One or both objects were not found."
            }

        object1 = doc1.to_dict()
        object2 = doc2.to_dict()

        prompt = f"""
Compare these two everyday objects as dating partners.

OBJECT 1
Name: {object1.get("name")}
Type: {object1.get("type")}
Personality: {object1.get("personality")}
Bio: {object1.get("bio")}

OBJECT 2
Name: {object2.get("name")}
Type: {object2.get("type")}
Personality: {object2.get("personality")}
Bio: {object2.get("bio")}

Give a funny compatibility analysis.

IMPORTANT:
Return exactly 6 lines.
Do not use JSON.
Do not use markdown.
Do not use emojis.

FORMAT:

SCORE: number from 0 to 100
VERDICT: one short sentence
CHEMISTRY: one short sentence
STRENGTHS: one short sentence
CONFLICTS: one short sentence
DATE: one short sentence

Keep every line short.
"""

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a funny compatibility analyst for everyday objects."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )

        text = response.choices[0].message.content.strip()

        print("\n===== GROQ COMPATIBILITY RESPONSE =====")
        print(text)
        print("========================================\n")

        # Default values
        score = 50
        verdict = "They might actually work."
        chemistry = "Their chemistry is surprisingly interesting."
        strengths = "They complement each other."
        conflicts = "They may have some unusual disagreements."
        perfect_date = "A quiet evening doing what they do best."

        # Read response line by line
        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip())
                except:
                    score = 50

            elif line.startswith("VERDICT:"):
                verdict = line.replace("VERDICT:", "").strip()

            elif line.startswith("CHEMISTRY:"):
                chemistry = line.replace("CHEMISTRY:", "").strip()

            elif line.startswith("STRENGTHS:"):
                strengths = line.replace("STRENGTHS:", "").strip()

            elif line.startswith("CONFLICTS:"):
                conflicts = line.replace("CONFLICTS:", "").strip()

            elif line.startswith("DATE:"):
                perfect_date = line.replace("DATE:", "").strip()

        # Keep score between 0 and 100
        score = max(0, min(100, score))

        compatibility = {
            "compatibility_score": score,
            "verdict": verdict,
            "chemistry": chemistry,
            "strengths": strengths,
            "conflicts": conflicts,
            "perfect_date": perfect_date
        }

        return {
            "status": "success",
            "compatibility": compatibility
        }

    except Exception as e:

        print("COMPATIBILITY ERROR:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }