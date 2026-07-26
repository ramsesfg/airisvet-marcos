const API_URL = "http://127.0.0.1:5000/api";

const estadoEl = document.getElementById("estado");
const formTicketEl = document.getElementById("form-tarea");
const inputTicketEl = document.getElementById("input-titulo");

const overlayEl = document.getElementById("panel-overlay");
const btnCerrarEl = document.getElementById("btn-cerrar-panel");
const formPerfilEl = document.getElementById("form-perfil");
const perfilIdEl = document.getElementById("perfil-id");
const perfilPerroEl = document.getElementById("perfil-perro");
const perfilRazaEl = document.getElementById("perfil-raza");
const perfilTamanoEl = document.getElementById("perfil-tamano");
const perfilDuenoEl = document.getElementById("perfil-dueno");
const perfilTelefonoEl = document.getElementById("perfil-telefono");
const perfilServicioEls = document.querySelectorAll('input[name="perfil-servicio"]');
const perfilFechaEl = document.getElementById("perfil-fecha");
const perfilHoraEl = document.getElementById("perfil-hora");
const btnGuardarEl = document.getElementById("btn-guardar-perfil");
const listaPerfilesEl = document.getElementById("lista-perfiles");

const mesAnteriorEl = document.getElementById("mes-anterior");
const mesSiguienteEl = document.getElementById("mes-siguiente");
const mesActualEl = document.getElementById("mes-actual");
const calendarioGridEl = document.getElementById("calendario-grid");
const citasDiaTituloEl = document.getElementById("citas-dia-titulo");
const citasDiaListaEl = document.getElementById("citas-dia-lista");
const btnAgendarDiaEl = document.getElementById("btn-agendar-dia");

const NOMBRES_MES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];
const DIAS_SEMANA = ["L", "M", "M", "J", "V", "S", "D"];

let perfilesActuales = [];
let diaSeleccionado = null;
const hoy = new Date();
const calendarioState = { anio: hoy.getFullYear(), mes: hoy.getMonth() }; // mes: 0-11

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

function abrirPanel() {
  overlayEl.classList.remove("hidden");
}

function cerrarPanel() {
  overlayEl.classList.add("hidden");
  formPerfilEl.reset();
  perfilServicioEls.forEach((chk) => (chk.checked = false));
  perfilIdEl.value = "";
  btnGuardarEl.textContent = "Guardar perfil";
}

async function cargarPerfiles() {
  try {
    const res = await fetch(`${API_URL}/perfiles`);
    const perfiles = await res.json();
    perfilesActuales = perfiles;
    renderizarPerfiles(perfiles);
    renderizarCalendario();
    if (diaSeleccionado) mostrarCitasDelDia(diaSeleccionado);
  } catch (err) {
    console.error("Error al cargar perfiles:", err);
  }
}

function renderizarPerfiles(perfiles) {
  listaPerfilesEl.innerHTML = "";
  perfiles.forEach((p) => {
    const li = document.createElement("li");

    const info = document.createElement("span");
    info.textContent = `${p.perro_nombre} — ${p.servicio || "sin servicio"} — ${p.fecha || "sin fecha"} ${p.hora || ""} — dueño: ${p.dueno_nombre}`;

    const acciones = document.createElement("div");
    acciones.className = "acciones";

    const btnEditar = document.createElement("button");
    btnEditar.textContent = "Editar";
    btnEditar.type = "button";
    btnEditar.onclick = () => cargarEnFormulario(p);

    const btnBorrar = document.createElement("button");
    btnBorrar.textContent = "Eliminar";
    btnBorrar.type = "button";
    btnBorrar.onclick = () => eliminarPerfil(p.id);

    acciones.appendChild(btnEditar);
    acciones.appendChild(btnBorrar);

    li.appendChild(info);
    li.appendChild(acciones);
    listaPerfilesEl.appendChild(li);
  });
}

function cargarEnFormulario(p) {
  perfilIdEl.value = p.id;
  perfilPerroEl.value = p.perro_nombre;
  perfilRazaEl.value = p.raza || "";
  perfilTamanoEl.value = p.tamano || "Pequeño";
  perfilDuenoEl.value = p.dueno_nombre;
  perfilTelefonoEl.value = p.dueno_telefono || "";

  const serviciosSeleccionados = (p.servicio || "").split(",").map((s) => s.trim());
  perfilServicioEls.forEach((chk) => {
    chk.checked = serviciosSeleccionados.includes(chk.value);
  });

  perfilFechaEl.value = p.fecha || "";
  perfilHoraEl.value = p.hora || "";
  btnGuardarEl.textContent = "Actualizar perfil";
  abrirPanel();
}

async function guardarPerfil(datos, id) {
  try {
    const url = id ? `${API_URL}/perfiles/${id}` : `${API_URL}/perfiles`;
    const method = id ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    if (!res.ok) throw new Error("Error al guardar perfil");
    await cargarPerfiles();
    formPerfilEl.reset();
    perfilServicioEls.forEach((chk) => (chk.checked = false));
    perfilIdEl.value = "";
    btnGuardarEl.textContent = "Guardar perfil";
  } catch (err) {
    console.error(err);
  }
}

async function eliminarPerfil(id) {
  try {
    await fetch(`${API_URL}/perfiles/${id}`, { method: "DELETE" });
    await cargarPerfiles();
  } catch (err) {
    console.error(err);
  }
}

// --- Calendario ---

function formatearFechaISO(anio, mes, dia) {
  const mm = String(mes + 1).padStart(2, "0");
  const dd = String(dia).padStart(2, "0");
  return `${anio}-${mm}-${dd}`;
}

function renderizarCalendario() {
  const { anio, mes } = calendarioState;
  mesActualEl.textContent = `${NOMBRES_MES[mes]} ${anio}`;

  const citasPorFecha = {};
  perfilesActuales.forEach((p) => {
    if (!p.fecha) return;
    citasPorFecha[p.fecha] = (citasPorFecha[p.fecha] || 0) + 1;
  });

  const primerDiaSemana = (new Date(anio, mes, 1).getDay() + 6) % 7; // lunes = 0
  const diasEnMes = new Date(anio, mes + 1, 0).getDate();

  calendarioGridEl.innerHTML = "";

  DIAS_SEMANA.forEach((d) => {
    const cabecera = document.createElement("div");
    cabecera.className = "dia-cabecera";
    cabecera.textContent = d;
    calendarioGridEl.appendChild(cabecera);
  });

  for (let i = 0; i < primerDiaSemana; i++) {
    calendarioGridEl.appendChild(document.createElement("div"));
  }

  for (let dia = 1; dia <= diasEnMes; dia++) {
    const fechaISO = formatearFechaISO(anio, mes, dia);
    const celda = document.createElement("button");
    celda.type = "button";
    celda.className = "dia-celda";
    if (fechaISO === diaSeleccionado) celda.classList.add("seleccionado");

    const numero = document.createElement("span");
    numero.textContent = dia;
    celda.appendChild(numero);

    if (citasPorFecha[fechaISO]) {
      const punto = document.createElement("span");
      punto.className = "dia-punto";
      punto.textContent = citasPorFecha[fechaISO];
      celda.appendChild(punto);
    }

    celda.onclick = () => {
      diaSeleccionado = fechaISO;
      renderizarCalendario();
      mostrarCitasDelDia(fechaISO);
    };

    calendarioGridEl.appendChild(celda);
  }
}

function mostrarCitasDelDia(fechaISO) {
  const citas = perfilesActuales
    .filter((p) => p.fecha === fechaISO)
    .sort((a, b) => (a.hora || "").localeCompare(b.hora || ""));

  citasDiaTituloEl.textContent = `Citas del ${fechaISO}`;
  citasDiaListaEl.innerHTML = "";
  btnAgendarDiaEl.classList.remove("hidden");

  if (citas.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No hay citas agendadas este día.";
    citasDiaListaEl.appendChild(li);
    return;
  }

  citas.forEach((p) => {
    const li = document.createElement("li");

    const info = document.createElement("span");
    info.textContent = `${p.hora || "sin hora"} — ${p.perro_nombre} (${p.servicio || "sin servicio"})`;

    const acciones = document.createElement("div");
    acciones.className = "acciones";

    const btnEditar = document.createElement("button");
    btnEditar.textContent = "Editar";
    btnEditar.type = "button";
    btnEditar.onclick = () => cargarEnFormulario(p);

    acciones.appendChild(btnEditar);
    li.appendChild(info);
    li.appendChild(acciones);
    citasDiaListaEl.appendChild(li);
  });
}

mesAnteriorEl.addEventListener("click", () => {
  calendarioState.mes -= 1;
  if (calendarioState.mes < 0) {
    calendarioState.mes = 11;
    calendarioState.anio -= 1;
  }
  renderizarCalendario();
});

mesSiguienteEl.addEventListener("click", () => {
  calendarioState.mes += 1;
  if (calendarioState.mes > 11) {
    calendarioState.mes = 0;
    calendarioState.anio += 1;
  }
  renderizarCalendario();
});

formTicketEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const nombre = inputTicketEl.value.trim();
  if (!nombre) return;
  perfilPerroEl.value = nombre;
  abrirPanel();
  inputTicketEl.value = "";
});

formPerfilEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const datos = {
    perro_nombre: perfilPerroEl.value.trim(),
    raza: perfilRazaEl.value.trim(),
    tamano: perfilTamanoEl.value,
    dueno_nombre: perfilDuenoEl.value.trim(),
    dueno_telefono: perfilTelefonoEl.value.trim(),
    servicio: Array.from(perfilServicioEls).filter((chk) => chk.checked).map((chk) => chk.value).join(", "),
    fecha: perfilFechaEl.value,
    hora: perfilHoraEl.value,
  };
  if (!datos.perro_nombre || !datos.dueno_nombre) return;
  guardarPerfil(datos, perfilIdEl.value || null);
});

btnCerrarEl.addEventListener("click", cerrarPanel);
overlayEl.addEventListener("click", (e) => {
  if (e.target === overlayEl) cerrarPanel();
});

// --- Botón "Agendar cita este día" (conecta calendario con panel de perfil) ---
btnAgendarDiaEl.addEventListener("click", () => {
  if (!diaSeleccionado) return;
  cerrarPanel(); // limpia cualquier residuo de un perfil anterior
  perfilFechaEl.value = diaSeleccionado;
  abrirPanel();
});

verificarBackend();
cargarPerfiles();

// --- Mini-galería del hero: soporte para tap en celulares ---
document.querySelectorAll(".mini-card").forEach((card) => {
  card.addEventListener("click", () => {
    const yaActiva = card.classList.contains("activa");
    document.querySelectorAll(".mini-card.activa").forEach((c) => c.classList.remove("activa"));
    if (!yaActiva) card.classList.add("activa");
  });
});