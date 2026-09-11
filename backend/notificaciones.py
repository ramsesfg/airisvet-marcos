import os
import requests


def enviar_notificacion_cita(nombre_mascota, nombre_dueno, fecha, hora, servicio=""):
    """
    Envía un correo al admin avisando que se creó una nueva cita.
    Usa la API HTTP de Brevo (no SMTP), para evitar el bloqueo de
    puertos SMTP en el plan gratuito de Render.
    """
    api_key = os.environ.get('BREVO_API_KEY')
    remitente = os.environ.get('EMAIL_REMITENTE')
    destinatario = os.environ.get('EMAIL_ADMIN')

    if not api_key or not remitente or not destinatario:
        print("⚠️ Faltan variables de entorno de correo (BREVO_API_KEY, EMAIL_REMITENTE o EMAIL_ADMIN), no se envió la notificación.")
        return False

    asunto = f"🐾 Nueva cita agendada - {nombre_mascota}"
    cuerpo_html = f"""
    <p>Se ha creado una nueva cita en Airisvet:</p>
    <ul>
      <li><strong>Mascota:</strong> {nombre_mascota}</li>
      <li><strong>Dueño:</strong> {nombre_dueno}</li>
      <li><strong>Fecha:</strong> {fecha}</li>
      <li><strong>Hora:</strong> {hora}</li>
      <li><strong>Servicio:</strong> {servicio or "No especificado"}</li>
    </ul>
    <p>Ingresa al panel de administración para más detalles.</p>
    """

    payload = {
        "sender": {"email": remitente, "name": "Airisvet"},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "htmlContent": cuerpo_html,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        # timeout corto para no bloquear el worker de Gunicorn si algo falla
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=8,
        )
        if response.status_code in (200, 201):
            print(f"✅ Notificación enviada correctamente (status {response.status_code}).")
            return True
        else:
            print(f"❌ Brevo respondió con error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar la notificación: {e}")
        return False