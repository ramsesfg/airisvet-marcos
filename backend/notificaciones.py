import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def enviar_notificacion_cita(nombre_mascota, nombre_dueno, fecha, hora, servicio=""):
    """
    Envía un correo al admin avisando que se creó una nueva cita.
    """
    remitente = os.environ.get('EMAIL_REMITENTE')
    password = os.environ.get('EMAIL_PASSWORD')
    destinatario = os.environ.get('EMAIL_ADMIN')

    if not remitente or not password or not destinatario:
        print("⚠️ Faltan variables de entorno de correo, no se envió la notificación.")
        return False

    asunto = f"🐾 Nueva cita agendada - {nombre_mascota}"
    cuerpo = f"""
    Se ha creado una nueva cita en Airisvet:

    Mascota: {nombre_mascota}
    Dueño: {nombre_dueno}
    Fecha: {fecha}
    Hora: {hora}
    Servicio: {servicio or "No especificado"}

    Ingresa al panel de administración para más detalles.
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(remitente, password)
            server.send_message(msg)
        print("✅ Notificación enviada correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al enviar la notificación: {e}")
        return False