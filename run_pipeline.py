# ==========================================================================================
# SEMINARIO DE GRADO II
# ESPECIALIZACIÓN EN CIENCIA DE DATOS
# Actividad 2.1: Estandarización de Pipelines y Control de Calidad de Datos

# ==========================================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================================================================

# Librerías para recibir argumentos, ejecutar las pruebas y registrar los resultados.
import argparse
import subprocess
import sys
import mlflow

from pathlib import Path
from time import perf_counter

# Importamos las funciones que desarrollamos en los otros archivos del proyecto.
from prepare import preparar_datos

from validate_data import (
    cargar_contrato,
    validar_dataset,
    mostrar_reporte
)

from train import entrenar_modelo

from tracking import (
    iniciar_ejecucion,
    registrar_calidad,
    registrar_etapa,
    registrar_entrenamiento,
    registrar_resultado_final
)


# ==========================================================================================
# 2. CONFIGURACIÓN DEL PROYECTO
# ==========================================================================================

# Obtenemos la ruta del proyecto para ejecutar las pruebas desde la carpeta correcta.
RUTA_PROYECTO = Path(__file__).resolve().parent

# Definimos el orden de las cuatro características del dataset Iris.
NOMBRES_CAMPOS = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
]


# ==========================================================================================
# 3. EJECUCIÓN DE PRUEBAS AUTOMATIZADAS
# ==========================================================================================

def ejecutar_pruebas():
    """
    Ejecuta las pruebas automatizadas mediante pytest,
    utilizando el mismo entorno virtual del pipeline.
    """

    # Usamos el mismo intérprete de Python con el que se está ejecutando el pipeline.
    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "test_pipeline.py",
            "-v"
        ],
        cwd=RUTA_PROYECTO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Mostramos en consola el resultado de las pruebas y los errores, si los hay.
    print(resultado.stdout)

    if resultado.stderr:
        print(resultado.stderr)

    # Guardar las evidencias de las pruebas en MLflow.
    mlflow.log_text(
        resultado.stdout + "\n" + resultado.stderr,
        "pruebas/resultados_pytest.txt"
    )

    # Guardamos el código de salida para identificar si pytest terminó correctamente.
    mlflow.log_metric(
        "pytest_exit_code",
        resultado.returncode
    )

    # Si alguna prueba falla, detenemos el proceso y dejamos registro del fallo.
    if resultado.returncode != 0:

        mlflow.set_tag(
            "tests_status",
            "RECHAZADAS"
        )

        raise RuntimeError(
            "Las pruebas automatizadas no fueron superadas."
        )

    mlflow.set_tag(
        "tests_status",
        "APROBADAS"
    )


# ==========================================================================================
# 4. ORQUESTACIÓN DEL PIPELINE
# ==========================================================================================

def ejecutar_pipeline(escenario="valido"):
    """
    Coordina automáticamente todas las etapas del pipeline.

    Escenarios disponibles:
    - valido: ejecución completa.
    - invalido: simulación controlada de errores.

    Códigos de salida:
    - 0: ejecución exitosa.
    - 1: ejecución rechazada o error.
    """

    # Tomamos el tiempo inicial para calcular cuánto dura toda la ejecución.
    inicio_pipeline = perf_counter()

    print("\n" + "=" * 70)
    print("PIPELINE AUTOMATIZADO - ACTIVIDAD 2.1")
    print("ESTANDARIZACIÓN Y CONTROL DE CALIDAD DE DATOS")
    print("=" * 70)

    print(f"Escenario seleccionado: {escenario.upper()}")

    # Crear una ejecución activa en MLflow antes de
    # comenzar las etapas del pipeline.

    with iniciar_ejecucion(escenario) as ejecucion:

        # Partimos de un estado de error hasta comprobar que todo terminó correctamente.
        codigo_salida = 1
        estado_final = "ERROR"
        entrenamiento_iniciado = False
        entrenamiento_completado = False

        # Al iniciar, todavía no se ha ejecutado ninguna prueba.
        mlflow.set_tag("tests_status", "NO_INICIADAS")

        try:

            # ==============================================================================
            # ETAPA 1. PREPARACIÓN DE DATOS
            # ==============================================================================

            print("\nETAPA 1. PREPARACIÓN DE DATOS")

            with registrar_etapa("preparacion"):

                # Preparamos los datos según el escenario seleccionado.
                registros, etiquetas = preparar_datos(
                    escenario
                )

                # Cargamos las reglas que deben cumplir los datos antes de entrenar.
                contrato = cargar_contrato()

                # Dejamos registrada la versión del contrato utilizada en esta ejecución.
                mlflow.set_tag(
                    "contract_version",
                    contrato["version"]
                )

                mlflow.log_param(
                    "dataset",
                    contrato["dataset"]
                )

                # Guardamos una copia del contrato como evidencia en MLflow.
                mlflow.log_dict(
                    contrato,
                    "calidad/data_contract.json"
                )


            # ==============================================================================
            # ETAPA 2. VALIDACIÓN Y CONTROL DE CALIDAD
            # ==============================================================================

            print("\nETAPA 2. VALIDACIÓN Y CONTROL DE CALIDAD")

            with registrar_etapa("validacion"):

                # Comparamos los registros y las etiquetas con las reglas del contrato.
                reporte = validar_dataset(
                    registros,
                    etiquetas,
                    contrato
                )

                # Mostramos el resultado de la validación y lo registramos en MLflow.
                mostrar_reporte(reporte)

                registrar_calidad(reporte)


            # ==============================================================================
            # QUALITY GATE - DECISIÓN DE CONTINUIDAD
            # ==============================================================================

            # Si los datos no cumplen las condiciones, no permitimos que el modelo se entrene.
            if not reporte["aprobado"]:

                mlflow.set_tag(
                    "etapa_validacion",
                    "RECHAZADA"
                )

                mlflow.set_tag(
                    "etapa_fallida",
                    "validacion"
                )

                # Dejamos constancia de que el entrenamiento y las pruebas no se ejecutaron.
                registrar_entrenamiento("BLOQUEADO")

                mlflow.set_tag(
                    "etapa_entrenamiento",
                    "NO_EJECUTADA"
                )

                mlflow.set_tag(
                    "etapa_pruebas",
                    "NO_EJECUTADA"
                )

                mlflow.set_tag(
                    "tests_status",
                    "NO_EJECUTADAS"
                )

                # Diferenciamos un rechazo por calidad de un error inesperado.
                estado_final = "RECHAZADO_POR_CALIDAD"

                print("\n" + "=" * 70)
                print("PIPELINE DETENIDO - QUALITY GATE")
                print("=" * 70)

                print("Los datos no cumplen el contrato.")
                print("Entrenamiento: BLOQUEADO")
                print("Pruebas posteriores: NO EJECUTADAS")
                print("Código de salida: 1")

                return 1


            # ==============================================================================
            # ETAPA 3. ENTRENAMIENTO Y EVALUACIÓN
            # ==============================================================================

            print("\nETAPA 3. ENTRENAMIENTO Y EVALUACIÓN")

            with registrar_etapa("entrenamiento"):

                # Organizamos las características respetando el orden definido al inicio.
                X = [
                    [
                        registro[campo]
                        for campo in NOMBRES_CAMPOS
                    ]
                    for registro in registros
                ]

                # Las etiquetas corresponden a las clases que el modelo debe aprender.
                y = etiquetas

                # Marcamos el inicio del entrenamiento para controlar posibles errores.
                entrenamiento_iniciado = True

                registrar_entrenamiento("EN_EJECUCION")

                # Entrenamos el modelo con los datos que ya superaron la validación.
                modelo, metricas = entrenar_modelo(X, y)

                # Si llegamos a este punto, el entrenamiento terminó correctamente.
                entrenamiento_completado = True

                registrar_entrenamiento("COMPLETADO")


            # ==============================================================================
            # ETAPA 4. PRUEBAS AUTOMATIZADAS
            # ==============================================================================

            print("\nETAPA 4. PRUEBAS AUTOMATIZADAS")

            with registrar_etapa("pruebas"):

                # Ejecutamos las pruebas para verificar el funcionamiento del pipeline.
                ejecutar_pruebas()


            # ==============================================================================
            # ETAPA 5. FINALIZACIÓN EXITOSA
            # ==============================================================================

            # Solo marcamos la ejecución como exitosa cuando todas las etapas se completan.
            estado_final = "EXITOSO"
            codigo_salida = 0

            print("\n" + "=" * 70)
            print("PIPELINE EJECUTADO CORRECTAMENTE")
            print("=" * 70)

            print("Preparación de datos: COMPLETADA")
            print("Control de calidad: APROBADO")
            print("Entrenamiento: COMPLETADO")
            print("Pruebas automatizadas: APROBADAS")
            print("Código de salida: 0")

            return 0


        # ==================================================================================
        # 5. MANEJO DE ERRORES
        # ==================================================================================

        # Capturamos los errores que puedan presentarse durante cualquier etapa.
        except Exception as error:

            estado_final = "ERROR"
            codigo_salida = 1

            # Si el error ocurrió durante el entrenamiento, actualizamos su estado.
            if entrenamiento_iniciado and not entrenamiento_completado:

                registrar_entrenamiento("ERROR")

            # Guardamos el detalle del error para poder revisarlo posteriormente.
            mlflow.log_text(
                str(error),
                "errores/error_pipeline.txt"
            )

            print("\n" + "=" * 70)
            print("ERROR DURANTE LA EJECUCIÓN DEL PIPELINE")
            print("=" * 70)

            print(f"Detalle: {error}")

            return 1


        # ==================================================================================
        # 6. REGISTRO FINAL DE TRAZABILIDAD
        # ==================================================================================

        # Este bloque se ejecuta incluso si el pipeline falla o se detiene por calidad.
        finally:

            # Calculamos el tiempo total y registramos el resultado de la ejecución.
            duracion_total = perf_counter() - inicio_pipeline

            registrar_resultado_final(
                estado_final,
                duracion_total,
                codigo_salida
            )

            # Diferenciar las ejecuciones exitosas de
            # las rechazadas o fallidas en MLflow.

            mlflow.end_run(
                status=(
                    "FINISHED"
                    if codigo_salida == 0
                    else "FAILED"
                )
            )

            print("\n" + "-" * 70)
            print("RESUMEN DE TRAZABILIDAD")
            print("-" * 70)

            print(f"Estado final: {estado_final}")
            print(f"Duración total: {duracion_total:.2f} segundos")
            # El identificador permite consultar esta ejecución específica en MLflow.
            print(f"Run ID: {ejecucion.info.run_id}")
            print("Resultados registrados en MLflow.")


# ==========================================================================================
# 7. CONFIGURACIÓN DE ARGUMENTOS Y PUNTO DE ENTRADA
# ==========================================================================================

# Este bloque se ejecuta únicamente cuando iniciamos el archivo directamente.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Pipeline automatizado de control "
            "de calidad del dataset Iris."
        )
    )

    # Permitimos elegir desde la consola si queremos probar datos válidos o inválidos.
    parser.add_argument(
        "--escenario",
        choices=["valido", "invalido"],
        default="valido",
        help="Seleccionar el escenario de ejecución."
    )

    # Leemos el escenario ingresado por el usuario.
    argumentos = parser.parse_args()

    try:

        codigo = ejecutar_pipeline(
            argumentos.escenario
        )

        # Devolvemos al sistema el código de salida que produjo el pipeline.
        sys.exit(codigo)

    except Exception as error:

        print(f"\nError general del pipeline: {error}")

        sys.exit(1)
