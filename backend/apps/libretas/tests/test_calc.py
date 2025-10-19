# backend/apps/libretas/tests/test_calc.py
from django.test import SimpleTestCase
from apps.libretas.services.calc_service import num_a_letra, redondear_2

class CalcTests(SimpleTestCase):
    def test_num_a_letra_basico(self):
        self.assertEqual(num_a_letra(18), "AD")
        self.assertEqual(num_a_letra(16.5), "A")
        self.assertEqual(num_a_letra(12.9), "B")
        self.assertEqual(num_a_letra(10), "C")

    def test_redondeo(self):
        self.assertEqual(redondear_2(12.345), 12.35)
        self.assertEqual(redondear_2(12.344), 12.34)
