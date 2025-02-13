import sqlite3
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialiser la base de données SQLite
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            user_id TEXT,
            last_used INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Ajouter une clé
@app.route('/add_key', methods=['POST'])
def add_key():
    data = request.json
    key = data.get("key")
    user_id = data.get("user")

    if key and user_id:
        conn = sqlite3.connect("keys.db")
        c = conn.cursor()
        c.execute("INSERT INTO keys (key, user_id, last_used) VALUES (?, ?, ?)", (key, user_id, int(time.time())))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Clé ajoutée."}), 200
    return jsonify({"status": "error", "message": "Données invalides"}), 400

# Supprimer une clé
@app.route('/remove_key', methods=['POST'])
def remove_key():
    data = request.json
    key = data.get("key")

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("DELETE FROM keys WHERE key = ?", (key,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Clé supprimée."}), 200

# Suppression automatique des clés après 10 jours
@app.route('/cleanup_keys', methods=['GET'])
def cleanup_keys():
    ten_days_ago = int(time.time()) - 10 * 24 * 60 * 60  # Timestamp il y a 10 jours
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("DELETE FROM keys WHERE last_used < ?", (ten_days_ago,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Anciennes clés supprimées."}), 200

# Route pour vérifier la clé
@app.route('/verify_key', methods=['POST'])
def verify_key():
    data = request.json
    key = data.get("key")
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("SELECT * FROM keys WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    
    if result:
        c.execute("UPDATE keys SET last_used = ? WHERE key = ?", (int(time.time()), key))
        conn.commit()
        return jsonify({"status": "success", "message": "Clé valide."}), 200
    else:
        return jsonify({"status": "error", "message": "Clé invalide."}), 401

if __name__ == "__main__":
    app.run(debug=True)
