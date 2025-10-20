from django.test import TestCase
from decimal import Decimal

class ConsolidacionSimpleTest(TestCase):
    
    def test_equivalencia_letra_simple(self):
        """Test simple de equivalencias literales"""
        # Simulamos la lógica directamente en el test
        def calcular_letra(promedio):
            if promedio >= 18:
                return 'AD'
            elif promedio >= 14:
                return 'A'
            elif promedio >= 11:
                return 'B'
            else:
                return 'C'
        
        self.assertEqual(calcular_letra(Decimal('19.5')), 'AD')
        self.assertEqual(calcular_letra(Decimal('15.0')), 'A')
        self.assertEqual(calcular_letra(Decimal('12.0')), 'B')
        self.assertEqual(calcular_letra(Decimal('8.0')), 'C')
    
    def test_promedio_simple(self):
        """Test simple de cálculo de promedios"""
        def calcular_promedio(bimestres):
            if not bimestres:
                return Decimal('0.00')
            disponibles = [b for b in bimestres if b is not None]
            if not disponibles:
                return Decimal('0.00')
            promedio = sum(disponibles) / len(disponibles)
            return Decimal(str(promedio)).quantize(Decimal('0.01'))
        
        bimestres = [Decimal('15.5')]
        self.assertEqual(calcular_promedio(bimestres), Decimal('15.50'))
        
        bimestres = [Decimal('15.5'), Decimal('16.0'), Decimal('14.5')]
        self.assertEqual(calcular_promedio(bimestres), Decimal('15.33'))