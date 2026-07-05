// URL base del backend. Cambiá esto cuando despliegues a producción.
const API_URL = "http://127.0.0.1:5000/api";

const estadoEl = document.getElementById("estado");
const listaEl = document.getElementById("lista-tareas");
const formEl = document.getElementById("form-tarea");
const inputEl = document.getElementById("input-titulo");

// --- Verifica que el backend esté disponible ---
async function verificarBackend() {
  try {
    const res = await fetch(`${API_URL}/health`);
    if (!res.ok) throw new Error();
    estadoEl.textContent = "✅ Sistema de reservas conectado";
    estadoEl.className = "estado ok";
  } catch (err) {
    estadoEl.textContent = "❌ No se pudo conectar al sistema de reservas (¿está corriendo el backend?)";
    estadoEl.className = "estado error";
  }
}

// --- Obtiene y renderiza las tareas ---
async function cargarTareas() {
  try {
    const res = await fetch(`${API_URL}/tareas`);
    const tareas = await res.json();
    renderizarTareas(tareas);
  } catch (err) {
    console.error("Error al cargar tareas:", err);
  }
}

function renderizarTareas(tareas) {
  listaEl.innerHTML = "";
  tareas.forEach((tarea) => {
    const li = document.createElement("li");

    const span = document.createElement("span");
    span.textContent = tarea.titulo;

    const btnBorrar = document.createElement("button");
    btnBorrar.textContent = "Eliminar";
    btnBorrar.onclick = () => eliminarTarea(tarea.id);

    li.appendChild(span);
    li.appendChild(btnBorrar);
    listaEl.appendChild(li);
  });
}

// --- Crea una nueva tarea ---
async function crearTarea(titulo) {
  try {
    const res = await fetch(`${API_URL}/tareas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ titulo }),
    });
    if (!res.ok) throw new Error("Error al crear tarea");
    await cargarTareas();
  } catch (err) {
    console.error(err);
  }
}

// --- Elimina una tarea ---
async function eliminarTarea(id) {
  try {
    await fetch(`${API_URL}/tareas/${id}`, { method: "DELETE" });
    await cargarTareas();
  } catch (err) {
    console.error(err);
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const titulo = inputEl.value.trim();
  if (!titulo) return;
  crearTarea(titulo);
  inputEl.value = "";
});

// --- Inicialización ---
verificarBackend();
cargarTareas();
