# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

import unittest
from unittest.mock import patch

from validate_data import cargar_contrato, validar_entrada
from run_pipeline import ejecutar_pipeline


# ============================================================
# 2. CONFIGURACIÓN DE LAS PRUEBAS
# ============================================================

class TestCalidadDatos(unittest.TestCase):

    def setUp(self):
        """
        Carga el contrato y define una entrada válida
        antes de ejecutar cada prueba.
        """

        self.contrato = cargar_contrato()

        self.datos_validos = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }


    # ========================================================
    # 3. PRUEBA 01: DATOS CORRECTOS
    # ========================================================

    def test_01_datos_validos(self):

        valido, errores = validar_entrada(
            self.datos_validos,
            self.contrato
        )

        self.assertTrue(valido)
        self.assertEqual(errores, [])


    # ========================================================
    # 4. PRUEBA 02: VALORES NULOS
    # ========================================================

    def test_02_valores_nulos(self):

        datos = self.datos_validos.copy()
        datos["sepal_length"] = None

        valido, errores = validar_entrada(
            datos,
            self.contrato
        )

        self.assertFalse(valido)
        self.assertTrue(
            any("nulos" in error for error in errores)
        )


    # ========================================================
    # 5. PRUEBA 03: TIPOS INCORRECTOS
    # ========================================================

    def test_03_tipos_incorrectos(self):

        datos = self.datos_validos.copy()
        datos["sepal_width"] = "abc"

        valido, errores = validar_entrada(
            datos,
            self.contrato
        )

        self.assertFalse(valido)
        self.assertTrue(
            any("numérico" in error for error in errores)
        )


    # ========================================================
    # 6. PRUEBA 04: VALORES FUERA DE RANGO
    # ========================================================

    def test_04_rangos_invalidos(self):

        datos = self.datos_validos.copy()
        datos["petal_length"] = -2.0

        valido, errores = validar_entrada(
            datos,
            self.contrato
        )

        self.assertFalse(valido)
        self.assertTrue(
            any("mínimo" in error for error in errores)
        )


    # ========================================================
    # 7. PRUEBA 05: BLOQUEO DEL PIPELINE
    # ========================================================

    def test_05_bloqueo_entrenamiento(self):
        """
        Simula un dataset con un registro incorrecto.

        Verifica que el pipeline rechace los datos y
        no invoque el entrenamiento.
        """

        datos_invalidos = [
            {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": -2.0,
                "petal_width": 0.2
            }
        ]

        # Sustituir temporalmente la carga de datos.
        with patch(
            "run_pipeline.cargar_dataset",
            return_value=(datos_invalidos, [0])
        ):

            # Vigilar que el entrenamiento no se ejecute.
            with patch(
                "run_pipeline.ejecutar_entrenamiento"
            ) as entrenamiento:

                resultado = ejecutar_pipeline()

                self.assertFalse(resultado)

                entrenamiento.assert_not_called()


# ============================================================
# 8. EJECUCIÓN DE LAS PRUEBAS
# ============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)