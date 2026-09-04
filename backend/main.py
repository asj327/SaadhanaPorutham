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


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is not set")

groq_client = Groq(api_key=groq_api_key)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="SaadhanaPorutham API")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "https://saadhana-porutham.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

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


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Welcome to SaadhanaPorutham API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# CREATE OBJECT MANUALLY
# ============================================================

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


# ============================================================
# GENERATE OBJECT PROFILE USING GROQ
# ============================================================

@app.post("/objects/generate")
def generate_object(object_type: str):

    prompt = f"""
Create a funny dating profile for this everyday object:

{object_type}

The app is called SaadhanaPorutham, where everyday objects date each other.

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

        # ----------------------------------------------------
        # GROQ REQUEST
        # ----------------------------------------------------

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create funny dating profiles "
                        "for everyday objects."
                    )
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

        # ----------------------------------------------------
        # REMOVE MARKDOWN CODE BLOCKS IF PRESENT
        # ----------------------------------------------------

        if profile_text.startswith("```json"):
            profile_text = profile_text[7:]

        elif profile_text.startswith("```"):
            profile_text = profile_text[3:]

        if profile_text.endswith("```"):
            profile_text = profile_text[:-3]

        profile_text = profile_text.strip()

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        profile = json.loads(profile_text)

        # ----------------------------------------------------
        # SAVE TO FIRESTORE
        # ----------------------------------------------------

        doc_ref = db.collection("objects").add({
            **profile,
            "created_at": datetime.now().isoformat()
        })

        object_id = doc_ref[1].id

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "status": "success",
            "object_id": object_id,
            "profile": json.dumps(profile)
        }

    except Exception as e:

        print("Groq/Firestore error:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# LIKE OBJECT
# ============================================================

@app.post("/objects/{object_id}/like")
def like_object(object_id: str):

    print("LIKE RECEIVED:", object_id)

    try:

        doc_ref = db.collection("likes").add({
            "object_id": object_id,
            "action": "like",
            "created_at": datetime.now().isoformat()
        })

        print(
            "FIRESTORE DOCUMENT CREATED:",
            doc_ref[1].id
        )

        return {
            "status": "success",
            "message": "Object liked",
            "document_id": doc_ref[1].id
        }

    except Exception as e:

        print("FIRESTORE ERROR:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# PASS OBJECT
# ============================================================

@app.post("/objects/{object_id}/pass")
def pass_object(object_id: str):

    print("PASS RECEIVED:", object_id)

    try:

        doc_ref = db.collection("likes").add({
            "object_id": object_id,
            "action": "pass",
            "created_at": datetime.now().isoformat()
        })

        print(
            "FIRESTORE DOCUMENT CREATED:",
            doc_ref[1].id
        )

        return {
            "status": "success",
            "message": "Object passed",
            "document_id": doc_ref[1].id
        }

    except Exception as e:

        print("FIRESTORE ERROR:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# GET ALL OBJECTS
# ============================================================

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

        print("GET OBJECTS ERROR:", repr(e))

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# JATHAKAM PORUTHAM
# ============================================================

@app.post("/objects/compatibility")
def check_compatibility(
    object1_id: str,
    object2_id: str
):

    try:

        # ====================================================
        # GET BOTH OBJECTS
        # ====================================================

        doc1 = (
            db
            .collection("objects")
            .document(object1_id)
            .get()
        )

        doc2 = (
            db
            .collection("objects")
            .document(object2_id)
            .get()
        )

        if not doc1.exists or not doc2.exists:

            return {
                "status": "error",
                "message": "One or both objects were not found."
            }

        object1 = doc1.to_dict()
        object2 = doc2.to_dict()


        # ====================================================
        # HELPER FUNCTION
        # ====================================================

        def keyword_score(text1, text2, keywords):

            text1 = str(text1 or "").lower()
            text2 = str(text2 or "").lower()

            matches = 0

            for word in keywords:

                if word in text1 and word in text2:
                    matches += 1

            return min(10, 4 + matches)


        # ====================================================
        # 1. DINA PORUTHAM
        # ====================================================

        dina = keyword_score(
            object1.get("bio"),
            object2.get("bio"),
            [
                "daily",
                "useful",
                "food",
                "work",
                "help",
                "clean",
                "carry",
                "hold",
                "store"
            ]
        )


        # ====================================================
        # 2. GANA PORUTHAM
        # ====================================================

        gana = keyword_score(
            object1.get("personality"),
            object2.get("personality"),
            [
                "calm",
                "funny",
                "friendly",
                "reliable",
                "practical",
                "organized",
                "playful",
                "loyal",
                "patient",
                "dependable"
            ]
        )


        # ====================================================
        # 3. MAHENDRA PORUTHAM
        # ====================================================

        mahendra = keyword_score(
            object1.get("green_flags"),
            object2.get("green_flags"),
            [
                "helpful",
                "reliable",
                "strong",
                "durable",
                "useful",
                "clean",
                "protect",
                "support",
                "dependable"
            ]
        )


        # ====================================================
        # 4. STHREE DEERGHA PORUTHAM
        # ====================================================

        sthree_deergha = keyword_score(
            object1.get("attachment_style"),
            object2.get("attachment_style"),
            [
                "commitment",
                "secure",
                "loyal",
                "stable",
                "dependable",
                "consistent",
                "long",
                "reliable"
            ]
        )


        # ====================================================
        # 5. YONI PORUTHAM
        # ====================================================

        type1 = str(
            object1.get("type", "")
        ).lower()

        type2 = str(
            object2.get("type", "")
        ).lower()

        yoni = 5

        compatible_pairs = [

            ("utensil", "kitchen"),
            ("utensil", "food"),
            ("cup", "drink"),
            ("bottle", "drink"),
            ("phone", "charger"),
            ("laptop", "charger"),
            ("laptop", "mouse"),
            ("chair", "desk"),
            ("backpack", "laptop"),
            ("notebook", "pen")

        ]

        for a, b in compatible_pairs:

            if (
                (a in type1 and b in type2)
                or
                (b in type1 and a in type2)
            ):

                yoni = 9

                break


        # ====================================================
        # 6. RASHI PORUTHAM
        # ====================================================

        if type1 == type2:

            rashi = 8

        elif (

            ("kitchen" in type1 and "kitchen" in type2)
            or
            ("electronic" in type1 and "electronic" in type2)
            or
            ("stationery" in type1 and "stationery" in type2)

        ):

            rashi = 9

        else:

            rashi = 6


        # ====================================================
        # 7. RASYADHIPATHI PORUTHAM
        # ====================================================

        rasyadhipathi = keyword_score(
            object1.get("personality"),
            object2.get("personality"),
            [
                "strong",
                "sharp",
                "calm",
                "smart",
                "practical",
                "creative",
                "reliable",
                "friendly",
                "bold",
                "patient"
            ]
        )


        # ====================================================
        # 8. VASYA PORUTHAM
        # ====================================================

        vasya = keyword_score(
            object1.get("love_language"),
            object2.get("love_language"),
            [
                "touch",
                "service",
                "attention",
                "support",
                "help",
                "quality",
                "time",
                "care",
                "useful"
            ]
        )


        # ====================================================
        # 9. RAJJU PORUTHAM
        # ====================================================

        rajju = keyword_score(
            object1.get("green_flags"),
            object2.get("green_flags"),
            [
                "durable",
                "strong",
                "sturdy",
                "stable",
                "reliable",
                "clean",
                "polished",
                "long-lasting",
                "dependable"
            ]
        )


        # ====================================================
        # 10. VEDHA PORUTHAM
        # ====================================================

        conflict_score = keyword_score(
            object1.get("turn_offs"),
            object2.get("turn_offs"),
            [
                "dirty",
                "broken",
                "messy",
                "scratch",
                "rust",
                "heat",
                "water",
                "noise",
                "pressure",
                "damage"
            ]
        )

        vedha = max(
            0,
            10 - conflict_score
        )


        # ====================================================
        # TOTAL SCORE
        # ====================================================

        total = (

            dina +
            gana +
            mahendra +
            sthree_deergha +
            yoni +
            rashi +
            rasyadhipathi +
            vasya +
            rajju +
            vedha

        )

        total = max(
            0,
            min(100, total)
        )


        # ====================================================
        # VERDICT
        # ====================================================

        if total >= 90:

            verdict = "Exceptional Porutham"

        elif total >= 80:

            verdict = "Excellent Porutham"

        elif total >= 70:

            verdict = "Good Porutham"

        elif total >= 60:

            verdict = "Moderate Porutham"

        elif total >= 40:

            verdict = "Challenging Porutham"

        else:

            verdict = "Porutham Not Found"


        # ====================================================
        # MARRIAGE PREDICTION
        # ====================================================

        marriage_prediction = (

            f"{object1.get('name')} and "
            f"{object2.get('name')} have a "
            f"{total}% chance of surviving "
            f"everyday object drama."

        )


        # ====================================================
        # EXPLANATIONS
        # ====================================================

        poruthams = {

            "dina": {

                "score": dina,

                "explanation":
                    f"{object1.get('name')} and "
                    f"{object2.get('name')} "
                    "fit surprisingly well into daily life."

            },

            "gana": {

                "score": gana,

                "explanation":
                    "Their personalities seem unusually compatible."

            },

            "mahendra": {

                "score": mahendra,

                "explanation":
                    "They actually make each other's jobs easier."

            },

            "sthree_deergha": {

                "score": sthree_deergha,

                "explanation":
                    "Their relationship has decent long-term potential."

            },

            "yoni": {

                "score": yoni,

                "explanation":
                    "Their physical purposes appear naturally compatible."

            },

            "rashi": {

                "score": rashi,

                "explanation":
                    "Their object categories have good cosmic chemistry."

            },

            "rasyadhipathi": {

                "score": rasyadhipathi,

                "explanation":
                    "Their dominant traits seem to cooperate nicely."

            },

            "vasya": {

                "score": vasya,

                "explanation":
                    "They appear capable of influencing each other positively."

            },

            "rajju": {

                "score": rajju,

                "explanation":
                    "The relationship appears reasonably stable and durable."

            },

            "vedha": {

                "score": vedha,

                "explanation":
                    "Their biggest conflicts are surprisingly manageable."

            }

        }


        # ====================================================
        # FINAL COMPATIBILITY OBJECT
        # ====================================================

        compatibility = {

            "object1": {

                "id": object1_id,
                "name": object1.get("name"),
                "type": object1.get("type")

            },

            "object2": {

                "id": object2_id,
                "name": object2.get("name"),
                "type": object2.get("type")

            },

            "poruthams": poruthams,

            "total_score": total,

            "verdict": verdict,

            "marriage_prediction":
                marriage_prediction

        }


        # ====================================================
        # SAVE COMPATIBILITY RESULT
        # ====================================================

        db.collection("compatibility").add({

            **compatibility,

            "created_at":
                datetime.now().isoformat()

        })


        # ====================================================
        # LOG
        # ====================================================

        print("\n===== JATHAKAM RESULT =====")
        print(compatibility)
        print("============================\n")


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "status": "success",

            "compatibility":
                compatibility

        }


    except Exception as e:

        print(
            "JATHAKAM ERROR:",
            repr(e)
        )

        return {

            "status": "error",

            "message":
                str(e)

        }