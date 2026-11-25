# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

# Se importa unittest para definir y ejecutar las pruebas automatizadas.
import unittest

# Se importan herramientas para simular funciones y objetos sin ejecutar
# procesos reales.
from unittest.mock import patch, MagicMock
# Se utiliza nullcontext para simular los contextos de ejecución del pipeline.
from contextlib import nullcontext

# Se importa el pipeline para comprobar el bloqueo del entrenamiento.
from run_pipeline import ejecutar_pipeline

# Se importa la preparación de datos para trabajar con ambos escenarios.
from prepare import preparar_datos

# Se importan las funciones encargadas de validar los datos y sus etiquetas.
from validate_data import (
    cargar_contrato,
    validar_entrada,
    validar_etiqueta,
    validar_dataset
)


# ============================================================
# 2. CONFIGURACIÓN DE LAS PRUEBAS
# ============================================================

# Se agrupan las pruebas relacionadas con el control de calidad de los datos.
class TestCalidadDatos(unittest.TestCase):

    def setUp(self):
        """
        Carga el contrato y una entrada válida antes
        de ejecutar cada prueba automatizada.
        """

        # Se carga el contrato antes de cada prueba para utilizar las mismas
        # reglas de validación.
        self.contrato = cargar_contrato()

        # Se define un registro válido que servirá como punto de partida para
        # las pruebas.
        self.datos_validos = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }


    # ========================================================
    # 3. VALIDACIÓN INDIVIDUAL DE REGISTROS
    # ========================================================

    # PRUEBA 01: Registro válido.

    def test_01_datos_validos(self):

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            self.datos_validos,
            self.contrato
        )

        # Se comprueba que el registro sea aceptado.
        self.assertTrue(valido)
        # Finalmente, se verifica que no se hayan identificado errores.
        self.assertEqual(errores, [])


    # PRUEBA 02: Valores nulos.

    def test_02_valores_nulos(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se asigna un valor nulo para comprobar que sea detectado.
        datos["sepal_length"] = None

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se comprueba que el mensaje de error haga referencia a los valores
        # nulos.
        self.assertTrue(
            any("nulos" in error for error in errores)
        )


    # PRUEBA 03: Tipos de datos incorrectos.

    def test_03_tipos_incorrectos(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se introduce texto en un campo que debe ser numérico.
        datos["sepal_width"] = "abc"

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se verifica que el error indique que se esperaba un dato numérico.
        self.assertTrue(
            any("numérico" in error for error in errores)
        )


    # PRUEBA 04: Valor inferior al mínimo.

    def test_04_rango_minimo(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se asigna un valor inferior al mínimo permitido.
        datos["petal_length"] = -2.0

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se comprueba que el mensaje haga referencia al límite mínimo.
        self.assertTrue(
            any("mínimo" in error for error in errores)
        )


    # PRUEBA 05: Valor superior al máximo.

    def test_05_rango_maximo(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se asigna un valor superior al máximo permitido.
        datos["petal_length"] = 15.0

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se comprueba que el mensaje haga referencia al límite máximo.
        self.assertTrue(
            any("máximo" in error for error in errores)
        )


    # PRUEBA 06: Campo obligatorio ausente.

    def test_06_campo_obligatorio(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se elimina una característica obligatoria para comprobar su
        # validación.
        del datos["sepal_length"]

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se verifica que el error indique la ausencia de un campo
        # obligatorio.
        self.assertTrue(
            any("obligatorio" in error for error in errores)
        )


    # PRUEBA 07: Campo adicional no permitido.

    def test_07_campo_adicional(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se agrega un campo que no está contemplado en el contrato.
        datos["campo_extra"] = 5.0

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se comprueba que el campo adicional sea identificado como no
        # permitido.
        self.assertTrue(
            any("no permitido" in error for error in errores)
        )


    # PRUEBA 08: Valores booleanos.

    def test_08_valores_booleanos(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se introduce un valor booleano en lugar de una medida numérica.
        datos["sepal_length"] = True

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se verifica que el mensaje indique que no se aceptan valores
        # booleanos.
        self.assertTrue(
            any("booleanos" in error for error in errores)
        )


    # PRUEBA 09: Valores NaN.

    def test_09_valores_nan(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se simula un valor NaN para comprobar que no sea aceptado.
        datos["sepal_length"] = float("nan")

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se comprueba que el mensaje indique que el valor debe ser finito.
        self.assertTrue(
            any("finito" in error for error in errores)
        )


    # PRUEBA 10: Valores infinitos.

    def test_10_valores_infinitos(self):

        # Se crea una copia del registro para no modificar los datos
        # originales.
        datos = self.datos_validos.copy()
        # Se introduce un valor infinito para comprobar la validación de
        # valores finitos.
        datos["sepal_length"] = float("inf")

        # Se valida el registro utilizando las condiciones definidas en el
        # contrato.
        valido, errores = validar_entrada(
            datos, self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Se verifica que el valor infinito genere el error correspondiente.
        self.assertTrue(
            any("finito" in error for error in errores)
        )


    # ========================================================
    # 4. VALIDACIÓN INTEGRAL DEL DATASET Y ETIQUETAS
    # ========================================================

    # PRUEBA 11: Dataset vacío.

    def test_11_dataset_vacio(self):

        # Se envían listas vacías para comprobar que el dataset no pueda
        # aprobarse sin registros.
        reporte = validar_dataset(
            [],
            [],
            self.contrato
        )

        # Se comprueba que el control de calidad no apruebe el conjunto de
        # datos.
        self.assertFalse(reporte["aprobado"])
        self.assertEqual(reporte["total_registros"], 0)

        # Se comprueba que el reporte indique que el dataset está vacío.
        self.assertTrue(
            any(
                "vacío" in error
                for error in reporte["errores_dataset"]
            )
        )


    # PRUEBA 12: Cantidad incorrecta de etiquetas.

    def test_12_correspondencia_etiquetas(self):

        # Se envía un registro sin su etiqueta para comprobar la
        # correspondencia entre ambos.
        reporte = validar_dataset(
            [self.datos_validos],
            [],
            self.contrato
        )

        # Se comprueba que el control de calidad no apruebe el conjunto de
        # datos.
        self.assertFalse(reporte["aprobado"])

        # Se verifica que el reporte identifique la diferencia en la cantidad
        # de etiquetas.
        self.assertTrue(
            any(
                "no coincide" in error
                for error in reporte["errores_dataset"]
            )
        )


    # PRUEBA 13: Etiqueta fuera de las clases permitidas.

    def test_13_etiqueta_fuera_de_clase(self):

        # Se utiliza una etiqueta que no pertenece a las clases permitidas.
        reporte = validar_dataset(
            [self.datos_validos],
            [5],
            self.contrato
        )

        # Se comprueba que el control de calidad no apruebe el conjunto de
        # datos.
        self.assertFalse(reporte["aprobado"])
        self.assertEqual(reporte["etiquetas_invalidas"], 1)


    # PRUEBA 14: Tipo incorrecto de etiqueta.

    def test_14_tipo_etiqueta_incorrecto(self):

        # Se valida una etiqueta de texto para comprobar que se exija un valor
        # entero.
        valido, error = validar_etiqueta(
            "setosa",
            self.contrato
        )

        # Se verifica que el dato incorrecto sea rechazado.
        self.assertFalse(valido)
        # Finalmente, se comprueba que el mensaje indique el tipo de dato
        # esperado.
        self.assertIn("entero", error)


    # PRUEBA 15: Dataset Iris válido completo.

    def test_15_dataset_valido_completo(self):

        # Se cargan los datos originales de Iris, sin introducir
        # modificaciones.
        registros, etiquetas = preparar_datos("valido")

        # Se valida el conjunto completo con las reglas del contrato.
        reporte = validar_dataset(
            registros,
            etiquetas,
            self.contrato
        )

        # Se comprueba que el dataset sea aprobado por el control de calidad.
        self.assertTrue(reporte["aprobado"])
        # Se revisan las cantidades de registros, los errores encontrados y el
        # porcentaje de calidad esperado.
        self.assertEqual(reporte["total_registros"], 150)
        self.assertEqual(reporte["registros_validos"], 150)
        self.assertEqual(reporte["registros_invalidos"], 0)
        self.assertEqual(reporte["etiquetas_invalidas"], 0)
        self.assertEqual(reporte["total_errores"], 0)
        self.assertEqual(reporte["porcentaje_calidad"], 100.0)


    # PRUEBA 16: Dataset con errores controlados.

    def test_16_dataset_invalido_completo(self):

        # Se prepara el dataset con los errores controlados del escenario
        # inválido.
        registros, etiquetas = preparar_datos("invalido")

        # Se valida el conjunto modificado para comprobar que se detecten los
        # errores introducidos.
        reporte = validar_dataset(
            registros,
            etiquetas,
            self.contrato
        )

        # Se comprueba que el control de calidad no apruebe el conjunto de
        # datos.
        self.assertFalse(reporte["aprobado"])
        # Se revisan las cantidades de registros, los errores encontrados y el
        # porcentaje de calidad esperado.
        self.assertEqual(reporte["total_registros"], 150)
        self.assertEqual(reporte["registros_validos"], 149)
        self.assertEqual(reporte["registros_invalidos"], 1)
        self.assertEqual(reporte["etiquetas_invalidas"], 0)
        self.assertEqual(reporte["total_errores"], 3)
        self.assertEqual(reporte["porcentaje_calidad"], 99.33)

    # ========================================================
    # 5. PRUEBA DE INTEGRACIÓN DEL QUALITY GATE
    # ========================================================

    # PRUEBA 17: Bloqueo automático del entrenamiento.

    def test_17_bloqueo_entrenamiento_pipeline(self):

        # Se crea una ejecución simulada para evitar generar registros reales
        # en MLflow.
        ejecucion_simulada = MagicMock()
        ejecucion_simulada.info.run_id = "test_quality_gate"

        # Se sustituyen temporalmente las funciones de seguimiento,
        # entrenamiento y pruebas para comprobar el comportamiento del
        # pipeline de forma aislada.
        with (
            patch(
                "run_pipeline.iniciar_ejecucion",
                return_value=nullcontext(ejecucion_simulada)
            ),
            patch(
                "run_pipeline.registrar_etapa",
                side_effect=lambda nombre: nullcontext()
            ),
            patch("run_pipeline.mlflow"),
            patch("run_pipeline.registrar_calidad"),
            patch(
                "run_pipeline.registrar_resultado_final"
            ) as resultado_final,
            patch(
                "run_pipeline.registrar_entrenamiento"
            ) as estado_entrenamiento,
            patch(
                "run_pipeline.entrenar_modelo"
            ) as entrenamiento,
            patch(
                "run_pipeline.ejecutar_pruebas"
            ) as pruebas
        ):

            # Se ejecuta el pipeline con datos incorrectos para comprobar que
            # el control de calidad detenga el proceso.
            codigo = ejecutar_pipeline("invalido")

            # Se comprueba que el pipeline retorne el código de salida 1.
            self.assertEqual(codigo, 1)

            # Se verifica que la función de entrenamiento no haya sido llamada.
            entrenamiento.assert_not_called()

            # Se comprueba que las pruebas posteriores
            # tampoco hayan sido ejecutadas.
            pruebas.assert_not_called()

            # Se verifica que el entrenamiento quede registrado como bloqueado.
            estado_entrenamiento.assert_called_once_with(
                "BLOQUEADO"
            )

            # Se comprueba que el resultado final se registre una sola vez.
            resultado_final.assert_called_once()

            # Se recuperan los argumentos del registro final para revisar el
            # estado y el código de salida.
            argumentos = resultado_final.call_args.args

            self.assertEqual(
                argumentos[0],
                "RECHAZADO_POR_CALIDAD"
            )

            # Finalmente, se confirma que el código de salida registrado
            # corresponda a una ejecución rechazada.
            self.assertEqual(argumentos[2], 1)

# ============================================================
# 6. EJECUCIÓN DE LAS PRUEBAS AUTOMATIZADAS
# ============================================================

# Se permite ejecutar este módulo de pruebas de forma independiente.
if __name__ == "__main__":

    # Finalmente, se ejecutan las pruebas y se muestra el resultado detallado
    # de cada una.
    unittest.main(verbosity=2)
