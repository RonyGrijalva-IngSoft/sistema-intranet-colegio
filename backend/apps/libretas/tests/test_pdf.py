# backend/apps/libretas/tests/test_pdf.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.libretas.services.pdf_service import render_bimestral_pdf, build_preview_dto

User = get_user_model()

class PdfSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.client = APIClient()
        self.client.login(username="tester", password="pass")

    def test_render_pdf_no_explota(self):
        dto = build_preview_dto(
            {"nivel": "Secundaria", "grado": "1ro", "seccion": 1, "curso": 1, "bimestre": "B1"},
            [{"alumnoId": "1", "alumno": "Alumno Demo", "nota_num": 14.0}]
        )
        pdf = render_bimestral_pdf(dto)
        self.assertTrue(len(pdf) > 1000)

    def test_endpoint_pdf(self):
        resp = self.client.post("/libretas/bimestral/pdf", {
            "nivel": "Secundaria",
            "grado": "1ro",
            "seccion": 1,
            "curso": 1,
            "bimestre": "B1",
            "descargaMasiva": False
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
