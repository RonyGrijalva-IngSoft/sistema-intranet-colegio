from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from .permissions import RolePermission, CanManageUGEL
from rest_framework.permissions import AllowAny
from .models import UGELDelegation, AuditLog, PasswordResetMock, Period
from .serializers import UGELDelegationSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

User = get_user_model()


class UGELDelegateCreateAPIView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['Directora']

    def post(self, request):
        tutor_id = request.data.get('tutor_id')
        tutor = get_object_or_404(User, pk=tutor_id)
        delegation = UGELDelegation.objects.create(tutor=tutor, delegated_by=request.user, active=True)
        AuditLog.objects.create(actor=request.user, action='delegate_ugel', target_type='User', target_id=str(tutor_id),
                                metadata={'delegation_id': delegation.id})
        serializer = UGELDelegationSerializer(delegation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UGELManageAPIView(APIView):
    permission_classes = [CanManageUGEL]

    def get(self, request):
        return Response({'detail': 'Acceso UGEL concedido'}, status=status.HTTP_200_OK)


class ClosePeriodAPIView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['Directora', 'Coordinador']

    def post(self, request, period_id):
        period = get_object_or_404(Period, pk=period_id)
        if getattr(period, 'closed', False):
            return Response({'detail': 'Periodo ya cerrado.'}, status=status.HTTP_409_CONFLICT)
        period.closed = True
        period.closed_by = request.user
        period.closed_at = timezone.now()
        period.save()
        AuditLog.objects.create(actor=request.user, action='close_period', target_type='Period', target_id=str(period_id))
        return Response({'detail': 'Periodo cerrado.'}, status=status.HTTP_200_OK)


class ExportPDFMockAPIView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['Directora', 'Coordinador', 'Tutor', 'Docente']

    def get(self, request, report_id=None):
        AuditLog.objects.create(actor=request.user, action='export_pdf', target_type='Report', target_id=str(report_id))
        return Response({'detail': 'PDF generado (mock).'}, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        token = PasswordResetMock.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(hours=1))
        return Response({'detail': 'Token creado (mock).', 'token': str(token.token)}, status=status.HTTP_201_CREATED)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data['token']
        new_password = ser.validated_data['password']
        pr = get_object_or_404(PasswordResetMock, token=token, used=False)
        if pr.expires_at and pr.expires_at < timezone.now():
            return Response({'detail': 'Token expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        user = pr.user
        user.set_password(new_password)
        user.save()
        pr.used = True
        pr.save()
        AuditLog.objects.create(actor=user, action='password_reset', target_type='User', target_id=str(user.pk))
        return Response({'detail': 'Contraseña actualizada (mock).'}, status=status.HTTP_200_OK)
