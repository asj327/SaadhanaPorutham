import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    decoded = base64.b64decode(firebase_credentials).decode("utf-8")
    firebase_config = json.loads(decoded)
    cred = credentials.Certificate(firebase_config)
else:
    cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(cred)

db = firestore.client()