"""
Plantilla backend con Flask
----------------------------
Servidor de ejemplo con:
- CORS configurado para el frontend
- Rutas organizadas con Blueprints
- Variables de entorno con python-dotenv
- Un endpoint de ejemplo que el frontend consume
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables desde .env

app = Flask(__name__)

# Configuración de CORS: en desarrollo permitimos el origen del frontend.
# En producción, restringí esto al dominio real de tu frontend.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")
CORS(app, origins=[FRONTEND_ORIGIN])

# --- Datos de ejemplo (simula una "base de datos" en memoria) ---
tareas = [
    {"id": 1, "titulo": "Aprender Flask", "hecha": False},
    {"id": 2, "titulo": "Conectar frontend con backend", "hecha": False},
]


@app.route("/api/health", methods=["GET"])
def health():
    """Endpoint simple para verificar que el server está vivo."""
    return jsonify({"status": "ok", "mensaje": "Backend funcionando 🚀"})


@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    return jsonify(tareas)


@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo", "").strip()

    if not titulo:
        return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400

    nueva = {
        "id": (tareas[-1]["id"] + 1) if tareas else 1,
        "titulo": titulo,
        "hecha": False,
    }
    tareas.append(nueva)
    return jsonify(nueva), 201


@app.route("/api/tareas/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    global tareas
    tareas = [t for t in tareas if t["id"] != tarea_id]
    return jsonify({"mensaje": "Tarea eliminada"}), 200


if __name__ == "__main__":
    # debug=True solo para desarrollo, nunca en producción
    app.run(debug=True, port=5000)
