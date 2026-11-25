# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

# Se importa MLflow para realizar el seguimiento y registro
# de los resultados obtenidos durante la ejecución del pipeline.
import mlflow

# Se utiliza Path para gestionar las rutas del proyecto.
from pathlib import Path

# Se importa contextmanager para controlar el inicio y la
# finalización de cada etapa del pipeline.
from contextlib import contextmanager

# Se utiliza perf_counter para medir los tiempos de ejecución.
from time import perf_counter


# ============================================================
# 2. CONFIGURACIÓN DE MLFLOW
# ============================================================

# Se obtiene la ruta donde se encuentra ubicado el proyecto.
RUTA_PROYECTO = Path(__file__).resolve().parent

# Se establece la ubicación de la base de datos local,
# donde se almacenará la información registrada en MLflow.
RUTA_BD = RUTA_PROYECTO / "mlflow.db"

# Se define el nombre del experimento correspondiente
# al desarrollo de la Actividad 2.1.
NOMBRE_EXPERIMENTO = "Actividad_2_1_Control_Calidad"


def configurar_mlflow():
    """
    Se establece la configuración de MLflow mediante una
    base de datos local y se selecciona el experimento
    en el que se almacenarán los resultados de las ejecuciones.
    """

    # Se configura SQLite como almacenamiento de seguimiento.
    mlflow.set_tracking_uri(
        f"sqlite:///{RUTA_BD.as_posix()}"
    )

    # Se selecciona el experimento definido anteriormente.
    # Si no existe, MLflow lo crea automáticamente.
    mlflow.set_experiment(NOMBRE_EXPERIMENTO)


# ============================================================
# 3. INICIO DE UNA EJECUCIÓN DEL PIPELINE
# ============================================================

def iniciar_ejecucion(escenario):
    """
    Se genera una ejecución independiente en MLflow para
    identificar y realizar el seguimiento de los resultados
    según el escenario seleccionado.
    """

    # Se realiza la configuración inicial de MLflow.
    configurar_mlflow()

    # Se establecen nombres diferentes para identificar
    # fácilmente las ejecuciones con datos válidos e inválidos.
    nombres = {
        "valido": "Pipeline_Datos_Validos",
        "invalido": "Pipeline_Datos_Invalidos"
    }

    # Se verifica que el escenario recibido corresponda
    # a una de las opciones previamente definidas.
    if escenario not in nombres:
        raise ValueError("Escenario no permitido.")

    # Se inicia una nueva ejecución y se asignan etiquetas
    # que permiten identificar la actividad, el escenario
    # y el estado inicial del pipeline y del entrenamiento.
    return mlflow.start_run(
        run_name=nombres[escenario],
        tags={
            "activity": "2.1",
            "execution_type": "automated_pipeline",
            "scenario": escenario,
            "pipeline_status": "EN_EJECUCION",
            "training_status": "NO_INICIADO"
        }
    )


# ============================================================
# 4. REGISTRO DE INDICADORES DE CALIDAD
# ============================================================

def registrar_calidad(reporte):
    """
    Se almacenan los resultados obtenidos durante la
    validación del dataset, con el propósito de contar
    con un historial de los indicadores de calidad.
    """

    # Se registran las métricas relacionadas con la cantidad
    # de registros, los errores identificados y el porcentaje
    # de calidad obtenido durante la validación.
    # El resultado del Quality Gate se representa mediante
    # un valor numérico: 1 si es aprobado y 0 si es rechazado.
    mlflow.log_metrics({
        "total_registros": reporte["total_registros"],
        "registros_validos": reporte["registros_validos"],
        "registros_invalidos": reporte["registros_invalidos"],
        "etiquetas_invalidas": reporte["etiquetas_invalidas"],
        "total_errores": reporte["total_errores"],
        "porcentaje_calidad": reporte["porcentaje_calidad"],
        "quality_gate": int(reporte["aprobado"])
    })

    # Se determina el estado de la validación teniendo en
    # cuenta el cumplimiento de las condiciones del contrato.
    estado = (
        "APROBADA"
        if reporte["aprobado"]
        else "RECHAZADA"
    )

    # Se registra el estado de la validación como una etiqueta
    # para facilitar su identificación dentro de MLflow.
    mlflow.set_tag("validation_status", estado)

    # Finalmente, se almacena el reporte completo en formato
    # JSON como evidencia del proceso de control de calidad.
    mlflow.log_dict(
        reporte,
        "calidad/reporte_calidad.json"
    )


# ============================================================
# 5. CONTROL Y MEDICIÓN DE LAS ETAPAS
# ============================================================

# Se utiliza el decorador contextmanager para realizar el
# seguimiento de cada etapa desde su inicio hasta su finalización.

@contextmanager
def registrar_etapa(nombre):
    """
    Se controla el estado y el tiempo de ejecución de cada
    etapa del pipeline, incluyendo los posibles errores
    que se presenten durante el proceso.
    """

    # Se registra el tiempo inicial de la etapa.
    inicio = perf_counter()

    # Se establece el estado inicial como EN_EJECUCION
    # para identificar que la etapa ha comenzado.
    mlflow.set_tag(
        f"etapa_{nombre}",
        "EN_EJECUCION"
    )

    try:

        # Se permite la ejecución de las instrucciones
        # correspondientes a la etapa actual.
        yield

    except Exception as error:

        # En caso de presentarse un error, se actualiza
        # el estado de la etapa para dejar constancia del fallo.
        mlflow.set_tag(
            f"etapa_{nombre}",
            "ERROR"
        )

        # Se registra el nombre de la etapa en la que
        # se presentó el inconveniente.
        mlflow.set_tag(
            "etapa_fallida",
            nombre
        )

        # Se almacena el detalle del error en un archivo
        # de texto para facilitar su posterior revisión.
        mlflow.log_text(
            str(error),
            f"errores/{nombre}.txt"
        )

        # Se propaga el error para que pueda ser controlado
        # desde la ejecución principal del pipeline.
        raise

    else:

        # Si no se presentan errores, se registra que
        # la etapa finalizó correctamente.
        mlflow.set_tag(
            f"etapa_{nombre}",
            "COMPLETADA"
        )

    finally:

        # Independientemente del resultado de la etapa,
        # se calcula el tiempo total empleado en su ejecución.
        duracion = perf_counter() - inicio

        # Finalmente, se registra la duración en segundos,
        # permitiendo consultar los tiempos de cada etapa.
        mlflow.log_metric(
            f"duracion_{nombre}_seg",
            round(duracion, 4)
        )


# ============================================================
# 6. REGISTRO DEL ESTADO DEL ENTRENAMIENTO
# ============================================================

def registrar_entrenamiento(estado):
    """
    Se realiza el seguimiento del estado del entrenamiento
    para identificar si fue iniciado, completado, bloqueado
    por el control de calidad o si presentó algún error.
    """

    # Se actualiza la etiqueta correspondiente al estado
    # del entrenamiento dentro de la ejecución activa.
    mlflow.set_tag(
        "training_status",
        estado
    )


# ============================================================
# 7. REGISTRO DEL RESULTADO FINAL
# ============================================================

def registrar_resultado_final(
    estado,
    duracion,
    codigo_salida
):
    """
    Se consolida el resultado general del pipeline,
    teniendo en cuenta su estado final, el tiempo total
    de ejecución y el código de salida obtenido.
    """

    # Se registra el estado final para identificar si el
    # pipeline fue exitoso, rechazado o presentó algún error.
    mlflow.set_tag(
        "pipeline_status",
        estado
    )

    # Se almacena el tiempo total de ejecución en segundos,
    # redondeado a cuatro cifras decimales.
    mlflow.log_metric(
        "duracion_total_seg",
        round(duracion, 4)
    )

    # Finalmente, se registra el código de salida,
    # donde 0 representa una ejecución exitosa y 1
    # corresponde a una ejecución rechazada o fallida.
    mlflow.log_metric(
        "exit_code",
        codigo_salida
    )


# ============================================================
# 8. VERIFICACIÓN INDEPENDIENTE DEL MÓDULO
# ============================================================

# Se permite ejecutar este módulo de manera independiente
# para comprobar la configuración de MLflow sin necesidad
# de ejecutar todas las etapas del pipeline.

if __name__ == "__main__":

    # Se realiza la configuración de MLflow.
    configurar_mlflow()

    # Se consulta el experimento mediante el nombre
    # establecido en la configuración inicial.
    experimento = mlflow.get_experiment_by_name(
        NOMBRE_EXPERIMENTO
    )

    # Se presenta en consola un resumen de la configuración
    # realizada en el módulo de trazabilidad.
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN DEL MÓDULO DE TRAZABILIDAD")
    print("=" * 60)

    # Se muestra la ubicación de la base de datos,
    # el nombre del experimento y su identificador.
    print(f"Base de datos: {RUTA_BD}")
    print(f"Experimento: {NOMBRE_EXPERIMENTO}")
    print(f"ID del experimento: {experimento.experiment_id}")

    # Finalmente, se muestra un mensaje de confirmación
    # indicando que la conexión con MLflow fue establecida.
    print("\nConexión con MLflow establecida correctamente.")

    print("=" * 60)