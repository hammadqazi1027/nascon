import os, time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "nascon"),
        user=os.getenv("DB_USER", "nascon"),
        password=os.getenv("DB_PASSWORD", "nascon123"),
    )

def init_db():
    for _ in range(30):
        try:
            c = conn(); cur = c.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
                phone TEXT, event TEXT NOT NULL, created_at TIMESTAMP DEFAULT NOW())""")
            c.commit(); c.close(); return
        except Exception as e:
            print("waiting for database:", e, flush=True)
            time.sleep(2)

init_db()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/register")
def register():
    d = request.get_json(silent=True) or {}
    if not d.get("name") or not d.get("email") or not d.get("event"):
        return jsonify(error="Name, email and event are required"), 400
    c = conn(); cur = c.cursor()
    cur.execute("INSERT INTO registrations (name,email,phone,event) VALUES (%s,%s,%s,%s) RETURNING id",
                (d["name"], d["email"], d.get("phone", ""), d["event"]))
    new_id = cur.fetchone()[0]
    c.commit(); c.close()
    return jsonify(id=new_id), 201

@app.get("/api/registrations")
def list_all():
    c = conn(); cur = c.cursor()
    cur.execute("SELECT id,name,email,phone,event,created_at FROM registrations ORDER BY id DESC")
    rows = [dict(id=r[0], name=r[1], email=r[2], phone=r[3], event=r[4], created_at=str(r[5])) for r in cur.fetchall()]
    c.close()
    return jsonify(rows)

@app.get("/api/registrations/count")
def count():
    c = conn(); cur = c.cursor()
    cur.execute("SELECT COUNT(*) FROM registrations")
    n = cur.fetchone()[0]; c.close()
    return jsonify(count=n)
