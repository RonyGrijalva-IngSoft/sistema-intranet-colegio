# backend/apps/libretas/views/ugel.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializers.ugel import UgelUploadIn
from ..services import ugel_service

class UgelExcelUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {"file": request.FILES.get("file")}
        ser = UgelUploadIn(data=data)
        ser.is_valid(raise_exception=True)
        f = ser.validated_data["file"]

        upload_id, saved_path = ugel_service.guardar_upload(f)
        hojas = ugel_service.inspeccionar_hojas(saved_path)
        # filename original se conserva (en saved_path)
        filename_original = f.name

        return JsonResponse(
            {"uploadId": upload_id, "filename": filename_original, "hojas": hojas},
            status=status.HTTP_201_CREATED
        )
