import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMessage
from django.conf import settings


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def contact_send(request):
    # Manejar preflight CORS
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"]  = settings.CORS_ALLOWED_ORIGIN
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "JSON invalido"}, status=400)

    # Validar campos requeridos
    nombre      = data.get("nombre", "").strip()
    correo      = data.get("correo", "").strip()
    telefono    = data.get("telefono", "").strip()
    asunto      = data.get("asunto", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not all([nombre, correo, asunto, descripcion]):
        return JsonResponse({"error": "Faltan campos obligatorios"}, status=400)

    # Armar el cuerpo del correo (solo ASCII-safe)
    cuerpo = (
        "Nuevo mensaje de contacto recibido desde citegra.com\n"
        "\n"
        "================================\n"
        "DATOS DEL REMITENTE\n"
        "================================\n"
        "\n"
        f"  Nombre:    {nombre}\n"
        f"  Correo:    {correo}\n"
        f"  Telefono:  {telefono if telefono else 'No proporcionado'}\n"
        "\n"
        "================================\n"
        "ASUNTO\n"
        "================================\n"
        "\n"
        f"  {asunto}\n"
        "\n"
        "================================\n"
        "DESCRIPCION DEL PROYECTO\n"
        "================================\n"
        "\n"
        f"{descripcion}\n"
        "\n"
        "================================\n"
        "Este mensaje fue enviado automaticamente desde el formulario de contacto.\n"
    )

    try:
        email = EmailMessage(
            subject=f"[Citegra Web] {asunto} - {nombre}",
            body=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECIPIENT_EMAIL],
        )
        email.encoding = 'utf-8'
        email.send(fail_silently=False)
    except Exception as e:
        traceback.print_exc()  # muestra error completo en terminal
        return JsonResponse({"error": f"Error al enviar correo: {str(e)}"}, status=500)

    response = JsonResponse({"ok": True, "mensaje": "Correo enviado correctamente"})
    response["Access-Control-Allow-Origin"] = settings.CORS_ALLOWED_ORIGIN
    return response