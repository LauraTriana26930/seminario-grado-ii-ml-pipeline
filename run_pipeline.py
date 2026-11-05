# ==========================================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================================================================

import sys

from sklearn.datasets import load_iris

from validate_data import cargar_contrato, validar_entrada
from train import entrenar_modelo


# ==========================================================================================
# 2. CONFIGURACIÓN DEL PROYECTO
# ==========================================================================================

# Definir los nombres y el orden de las características
# utilizadas tanto en el contrato como en el modelo.

NOMBRES_CAMPOS = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
]


# ==========================================================================================
# 3. CARGA DEL DATASET IRIS
# ==========================================================================================

def cargar_dataset():
    """
    Carga el dataset Iris una sola vez.

    Retorna:
    - registros: características organizadas como diccionarios.
    - etiquetas: especies correspondientes a cada registro.
    """

    dataset = load_iris()

    registros = []

    for fila in dataset.data:

        registro = {
            nombre: float(valor)
            for nombre, valor in zip(NOMBRES_CAMPOS, fila)
        }

        registros.append(registro)

    etiquetas = dataset.target

    return registros, etiquetas


# ==========================================================================================
# 4. VALIDACIÓN DE CALIDAD DEL DATASET
# ==========================================================================================

def validar_dataset(registros, contrato):
    """
    Valida todos los registros utilizando las reglas
    definidas en data_contract.json.

    Retorna True únicamente cuando todos los registros
    cumplen el contrato de datos.
    """

    total_validos = 0
    total_invalidos = 0

    for numero, registro in enumerate(registros, start=1):

        es_valido, errores = validar_entrada(
            registro,
            contrato
        )

        if es_valido:

            total_validos += 1

        else:

            total_invalidos += 1

            print(f"\nRegistro {numero}: RECHAZADO")

            for error in errores:
                print(f"  - {error}")

    # Presentar el resumen de calidad.
    print("\n" + "-" * 60)
    print("RESUMEN DEL CONTROL DE CALIDAD")
    print("-" * 60)

    print(f"Total de registros: {len(registros)}")
    print(f"Registros válidos: {total_validos}")
    print(f"Registros inválidos: {total_invalidos}")

    return total_invalidos == 0 and len(registros) > 0


# ==========================================================================================
# 5. EJECUCIÓN AUTOMÁTICA DEL ENTRENAMIENTO
# ==========================================================================================

def ejecutar_entrenamiento(X, y):
    """
    Ejecuta Random Forest utilizando directamente
    los datos que superaron la validación.
    """

    print("\nIniciando entrenamiento de Random Forest...")

    modelo, accuracy = entrenar_modelo(X, y)

    print(f"Entrenamiento finalizado. Accuracy: {accuracy}")

    return True


# ==========================================================================================
# 6. ORQUESTACIÓN DEL PIPELINE
# ==========================================================================================

def ejecutar_pipeline():
    """
    Coordina la carga, validación y entrenamiento.

    El modelo únicamente se entrena cuando todos los
    registros cumplen las condiciones del contrato.
    """

    print("\n" + "=" * 60)
    print("PIPELINE AUTOMATIZADO - DATASET IRIS")
    print("=" * 60)

    # ======================================================================================
    # ETAPA 1. CARGA DE DATOS
    # ======================================================================================

    print("\nETAPA 1. CARGA DE DATOS")

    registros, etiquetas = cargar_dataset()
    contrato = cargar_contrato()

    print("Dataset Iris cargado correctamente.")
    print("Contrato de datos cargado correctamente.")

    # ======================================================================================
    # ETAPA 2. VALIDACIÓN DE CALIDAD
    # ======================================================================================

    print("\nETAPA 2. VALIDACIÓN DE CALIDAD")

    datos_validos = validar_dataset(
        registros,
        contrato
    )

    if not datos_validos:

        print("\nPIPELINE DETENIDO")
        print("Se encontraron errores en los datos.")
        print("El modelo NO será entrenado.")

        return False

    # Verificar que las etiquetas correspondan a los registros.
    if len(registros) != len(etiquetas):

        print("\nPIPELINE DETENIDO")
        print("La cantidad de registros y etiquetas no coincide.")

        return False

    print("\nVALIDACIÓN EXITOSA")
    print("Todos los registros cumplen el contrato.")

    # ======================================================================================
    # ETAPA 3. PREPARACIÓN DE DATOS VALIDADOS
    # ======================================================================================

    # Construir X a partir de los registros ya validados.
    # Se conserva el orden de características del modelo.

    X = [
        [registro[campo] for campo in NOMBRES_CAMPOS]
        for registro in registros
    ]

    # Mantener las etiquetas asociadas a los registros.
    y = etiquetas

    print("\nDatos preparados para el entrenamiento.")
    print(f"Total de muestras: {len(X)}")
    print(f"Características por muestra: {len(NOMBRES_CAMPOS)}")

    # ======================================================================================
    # ETAPA 4. ENTRENAMIENTO Y REGISTRO EN MLFLOW
    # ======================================================================================

    print("\nETAPA 4. ENTRENAMIENTO Y REGISTRO EN MLFLOW")

    entrenamiento_exitoso = ejecutar_entrenamiento(X, y)

    if not entrenamiento_exitoso:

        print("\nPIPELINE FINALIZADO CON ERROR")
        print("No fue posible completar el entrenamiento.")

        return False

    # ======================================================================================
    # ETAPA 5. FINALIZACIÓN
    # ======================================================================================

    print("\n" + "=" * 60)
    print("PIPELINE EJECUTADO CORRECTAMENTE")
    print("Validación y entrenamiento finalizados.")
    print("=" * 60)

    return True


# ==========================================================================================
# 7. PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================================================

if __name__ == "__main__":

    try:

        resultado = ejecutar_pipeline()

        sys.exit(0 if resultado else 1)

    except Exception as error:

        print("\nERROR DURANTE LA EJECUCIÓN DEL PIPELINE")
        print(f"Detalle: {error}")

        sys.exit(1)