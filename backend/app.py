from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

app = Flask(__name__)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")
CORS(app, origins=[FRONTEND_ORIGIN])

DB_PATH = os.path.join(os.path.dirname(__file__), "arisvet.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            perro_nombre TEXT NOT NULL,
            raza TEXT,
            tamano TEXT,
            dueno_nombre TEXT NOT NULL,
            dueno_telefono TEXT,
            servicio TEXT,
            fecha TEXT,
            hora TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Migración: si la tabla ya existía sin estas columnas, las agrega.
    columnas_existentes = [fila["name"] for fila in conn.execute("PRAGMA table_info(perfiles)").fetchall()]
    for columna in ("servicio", "fecha", "hora"):
        if columna not in columnas_existentes:
            conn.execute(f"ALTER TABLE perfiles ADD COLUMN {columna} TEXT")
    conn.commit()
    conn.close()
init_db()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mensaje": "Backend funcionando 🚀"})


@app.route("/api/perfiles", methods=["GET"])
def obtener_perfiles():
    conn = get_db()
    filas = conn.execute("SELECT * FROM perfiles ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas])

@app.route("/api/perfiles", methods=["POST"])
def crear_perfil():
    data = request.get_json(silent=True) or {}
    perro_nombre = data.get("perro_nombre", "").strip()
    dueno_nombre = data.get("dueno_nombre", "").strip()

    if not perro_nombre or not dueno_nombre:
        return jsonify({"error": "Los campos 'perro_nombre' y 'dueno_nombre' son obligatorios"}), 400

    conn = get_db()
    cur = conn.execute(
        """INSERT INTO perfiles
           (perro_nombre, raza, tamano, dueno_nombre, dueno_telefono, servicio, fecha, hora)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            perro_nombre,
            data.get("raza", ""),
            data.get("tamano", ""),
            dueno_nombre,
            data.get("dueno_telefono", ""),
            data.get("servicio", ""),
            data.get("fecha", ""),
            data.get("hora", ""),
        ),
    )
    conn.commit()
    nuevo = conn.execute("SELECT * FROM perfiles WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(nuevo)), 201

@app.route("/api/perfiles/<int:perfil_id>", methods=["PUT"])
def actualizar_perfil(perfil_id):
    data = request.get_json(silent=True) or {}
    perro_nombre = data.get("perro_nombre", "").strip()
    dueno_nombre = data.get("dueno_nombre", "").strip()

    if not perro_nombre or not dueno_nombre:
        return jsonify({"error": "Los campos 'perro_nombre' y 'dueno_nombre' son obligatorios"}), 400

    conn = get_db()
    conn.execute(
        """UPDATE perfiles SET
           perro_nombre = ?, raza = ?, tamano = ?, dueno_nombre = ?, dueno_telefono = ?,
           servicio = ?, fecha = ?, hora = ?
           WHERE id = ?""",
        (
            perro_nombre,
            data.get("raza", ""),
            data.get("tamano", ""),
            dueno_nombre,
            data.get("dueno_telefono", ""),
            data.get("servicio", ""),
            data.get("fecha", ""),
            data.get("hora", ""),
            perfil_id,
        ),
    )
    conn.commit()
    actualizado = conn.execute("SELECT * FROM perfiles WHERE id = ?", (perfil_id,)).fetchone()
    conn.close()

    if not actualizado:
        return jsonify({"error": "Perfil no encontrado"}), 404

    return jsonify(dict(actualizado)), 200


@app.route("/api/perfiles/<int:perfil_id>", methods=["DELETE"])
def eliminar_perfil(perfil_id):
    conn = get_db()
    conn.execute("DELETE FROM perfiles WHERE id = ?", (perfil_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Perfil eliminado"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)