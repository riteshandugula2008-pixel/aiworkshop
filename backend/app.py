import os
from uuid import UUID

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from postgrest import APIError
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)
# This API is intentionally public: any origin may make browser requests.


@app.after_request
def add_cors_headers(response):
    if request.path.startswith("/api/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
supabase: Client | None = (
    create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
)


def database():
    if supabase is None:
        return None, (jsonify(error="Supabase is not configured"), 500)
    return supabase, None


def valid_uuid(value):
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        return None


def api_error(error):
    return jsonify(error=getattr(error, "message", str(error))), 500


@app.get("/")
def index():
    return jsonify(message="Events API", endpoints=[
        "GET /api/events",
        "GET /api/events/<id>",
        "POST /api/registrations",
        "GET /api/me/registrations?user_id=<uuid>",
        "GET /api/events/<id>/registrations?organizer_id=<uuid>",
    ])


@app.get("/api/events")
def list_events():
    client, error = database()
    if error:
        return error
    try:
        response = client.table("events").select("*").execute()
        return jsonify(response.data)
    except APIError as exc:
        return api_error(exc)


@app.get("/api/events/<event_id>")
def get_event(event_id):
    event_id = valid_uuid(event_id)
    if event_id is None:
        return jsonify(error="id must be a valid UUID"), 400
    client, error = database()
    if error:
        return error
    try:
        response = client.table("events").select("*").eq("id", event_id).limit(1).execute()
        if not response.data:
            return jsonify(error="Event not found"), 404
        return jsonify(response.data[0])
    except APIError as exc:
        return api_error(exc)


@app.post("/api/registrations")
def create_registration():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    user_id = valid_uuid(body.get("user_id"))
    event_id = valid_uuid(body.get("event_id"))
    if user_id is None or event_id is None:
        return jsonify(error="user_id and event_id must be valid UUIDs"), 400

    client, error = database()
    if error:
        return error
    try:
        existing = (
            client.table("registrations")
            .select("id")
            .eq("user_id", user_id)
            .eq("event_id", event_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            return jsonify(error="User is already registered for this event"), 409

        created = client.table("registrations").insert(
            {"user_id": user_id, "event_id": event_id}
        ).execute()
        return jsonify(created.data[0]), 201
    except APIError as exc:
        return api_error(exc)


@app.get("/api/me/registrations")
def my_registrations():
    # With authentication disabled there is no session identity; caller supplies the user UUID.
    user_id = valid_uuid(request.args.get("user_id"))
    if user_id is None:
        return jsonify(error="A valid user_id query parameter is required"), 400

    client, error = database()
    if error:
        return error
    try:
        response = (
            client.table("registrations")
            .select("*, events(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return jsonify(response.data)
    except APIError as exc:
        return api_error(exc)


@app.get("/api/events/<event_id>/registrations")
def event_registrations(event_id):
    event_id = valid_uuid(event_id)
    organizer_id = valid_uuid(request.args.get("organizer_id"))
    if event_id is None or organizer_id is None:
        return jsonify(error="Valid event id and organizer_id are required"), 400

    client, error = database()
    if error:
        return error
    try:
        event = (
            client.table("events")
            .select("id, organizer_id")
            .eq("id", event_id)
            .limit(1)
            .execute()
        )
        if not event.data:
            return jsonify(error="Event not found"), 404
        if event.data[0]["organizer_id"] != organizer_id:
            return jsonify(error="Only the event organizer may view attendees"), 403

        response = (
            client.table("registrations")
            .select("*, users(id, email, role)")
            .eq("event_id", event_id)
            .execute()
        )
        return jsonify(response.data)
    except APIError as exc:
        return api_error(exc)


if __name__ == "__main__":
    app.run(debug=True)
