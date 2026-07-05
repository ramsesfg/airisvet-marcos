# Plantilla Frontend + Backend (Flask)

Boilerplate simple sin dependencias de npm. El frontend es HTML/CSS/JS puro,
el backend es Flask (Python).

## Estructura

```
plantilla-web/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## Cómo correr el backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

El backend queda corriendo en `http://127.0.0.1:5000`.

## Cómo correr el frontend

No necesita build ni instalación. Opciones:

1. **Más simple**: abrí `frontend/index.html` directo en el navegador
   (aunque para que CORS funcione bien, mejor usar la opción 2).
2. **Recomendado**: usá la extensión "Live Server" de VS Code, o corré:
   ```bash
   cd frontend
   python3 -m http.server 5500
   ```
   y entrá a `http://127.0.0.1:5500`.

Si usás otro puerto, actualizá `FRONTEND_ORIGIN` en `backend/.env` y
`API_URL` en `frontend/script.js`.

## Qué incluye de ejemplo

Un mini CRUD de "tareas" para que veas el patrón de comunicación
frontend ↔ backend:

- `GET /api/health` — chequeo de que el server está vivo
- `GET /api/tareas` — lista tareas
- `POST /api/tareas` — crea una tarea (`{ "titulo": "..." }`)
- `DELETE /api/tareas/<id>` — elimina una tarea

Las tareas viven en memoria (una lista de Python), así que se reinician
cada vez que reiniciás el servidor. Cuando quieras persistencia real,
lo siguiente es sumar SQLite con `sqlite3` o `SQLAlchemy`.

## Próximos pasos sugeridos

- Agregar una base de datos real (SQLite para empezar).
- Agregar autenticación (JWT con `flask-jwt-extended`).
- Separar rutas en Blueprints si el proyecto crece.
- Validar y sanitizar inputs más estrictamente contra inyección.
