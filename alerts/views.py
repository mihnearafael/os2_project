import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Alert


def dashboard(request):
    alerts = Alert.objects.all().order_by('-timestamp')
    return render(request, 'alerts/dashboard.html', {'alerts': alerts})

@csrf_exempt
def receive_alert(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Alert.objects.create(
                file_path=data.get('file_path', 'Unknown'),
                message=data.get('message', 'No message'),
                content=data.get('content', '')
            )
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=405)