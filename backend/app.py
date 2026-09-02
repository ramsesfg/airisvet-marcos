from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import os
from notificaciones import enviar_notificacion_cita

load_dotenv()

app = Flask(__name__)

# FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")
# CORS(app, origins=[FRONTEND_ORIGIN])

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id SERIAL PRIMARY KEY,
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
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'perfiles'
    """)
    columnas_existentes = [fila["column_name"] for fila in cur.fetchall()]
    for columna in ("servicio", "fecha", "hora"):
        if columna not in columnas_existentes:
            cur.execute(f"ALTER TABLE perfiles ADD COLUMN {columna} TEXT")
    conn.commit()
    cur.close()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mensaje": "Backend funcionando 🚀"})


@app.route("/api/perfiles", methods=["GET"])
def obtener_perfiles():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM perfiles ORDER BY id DESC")
    filas = cur.fetchall()
    cur.close()
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
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO perfiles
           (perro_nombre, raza, tamano, dueno_nombre, dueno_telefono, servicio, fecha, hora)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING id""",
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
    nuevo_id = cur.fetchone()["id"]
    conn.commit()

    cur.execute("SELECT * FROM perfiles WHERE id = %s", (nuevo_id,))
    nuevo = cur.fetchone()
    cur.close()
    conn.close()

    # Enviar notificación por correo al admin (no bloquea la respuesta si falla)
    enviar_notificacion_cita(
        nombre_mascota=perro_nombre,
        nombre_dueno=dueno_nombre,
        fecha=data.get("fecha", ""),
        hora=data.get("hora", ""),
        servicio=data.get("servicio", ""),
    )

    return jsonify(dict(nuevo)), 201


@app.route("/api/perfiles/<int:perfil_id>", methods=["PUT"])
def actualizar_perfil(perfil_id):
    data = request.get_json(silent=True) or {}
    perro_nombre = data.get("perro_nombre", "").strip()
    dueno_nombre = data.get("dueno_nombre", "").strip()

    if not perro_nombre or not dueno_nombre:
        return jsonify({"error": "Los campos 'perro_nombre' y 'dueno_nombre' son obligatorios"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """UPDATE perfiles SET
           perro_nombre = %s, raza = %s, tamano = %s, dueno_nombre = %s, dueno_telefono = %s,
           servicio = %s, fecha = %s, hora = %s
           WHERE id = %s""",
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

    cur.execute("SELECT * FROM perfiles WHERE id = %s", (perfil_id,))
    actualizado = cur.fetchone()
    cur.close()
    conn.close()

    if not actualizado:
        return jsonify({"error": "Perfil no encontrado"}), 404

    return jsonify(dict(actualizado)), 200


@app.route("/api/perfiles/<int:perfil_id>", methods=["DELETE"])
def eliminar_perfil(perfil_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM perfiles WHERE id = %s", (perfil_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Perfil eliminado"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)