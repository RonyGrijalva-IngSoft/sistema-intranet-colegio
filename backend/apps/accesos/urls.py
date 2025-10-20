from django.urls import path
from .views import UGELDelegateCreateAPIView, UGELManageAPIView, ClosePeriodAPIView, ExportPDFMockAPIView, PasswordResetRequestAPIView, PasswordResetConfirmAPIView

urlpatterns = [
    path('ugel/delegate/', UGELDelegateCreateAPIView.as_view(), name='accesos-ugel-delegate'),
    path('ugel/manage/', UGELManageAPIView.as_view(), name='accesos-ugel-manage'),
    path('period/<int:period_id>/close/', ClosePeriodAPIView.as_view(), name='accesos-close-period'),
    path('export/pdf/<int:report_id>/', ExportPDFMockAPIView.as_view(), name='accesos-export-pdf'),
    path('auth/password-reset/', PasswordResetRequestAPIView.as_view(), name='accesos-password-reset-request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='accesos-password-reset-confirm'),
]
