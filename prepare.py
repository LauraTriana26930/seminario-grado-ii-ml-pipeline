# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

# Se importa argparse para permitir la selección del escenario
# de ejecución desde la terminal.
import argparse

# Se importa el dataset Iris desde la librería Scikit-learn.
from sklearn.datasets import load_iris


# ============================================================
# 2. CONFIGURACIÓN DE CARACTERÍSTICAS
# ============================================================

# Se definen los nombres de las cuatro características del
# dataset Iris para mantener una estructura estandarizada.

NOMBRES_CAMPOS = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
]


# ============================================================
# 3. PREPARACIÓN DEL DATASET
# ============================================================

def preparar_datos(escenario="valido"):
    """
    Esta función permite cargar y preparar los datos del
    dataset Iris para su posterior validación.

    Se establecen dos escenarios:
    - valido: se utilizan los datos originales.
    - invalido: se introducen errores de manera controlada
      para comprobar el funcionamiento del control de calidad.

    Finalmente, se retornan los registros preparados
    y sus respectivas etiquetas.
    """

    # Se verifica que el escenario seleccionado corresponda
    # a una de las opciones permitidas.
    if escenario not in ("valido", "invalido"):
        raise ValueError("Escenario no permitido.")

    # Se realiza la carga del dataset Iris.
    dataset = load_iris()

    # Se inicializa una lista vacía para almacenar los
    # registros que serán procesados.
    registros = []

    # Se recorre cada una de las filas del dataset.
    for fila in dataset.data:

        # Se organiza cada registro en un diccionario,
        # relacionando el nombre de cada característica
        # con su respectivo valor.
        # Los valores se convierten a float para mantener
        # un tipo de dato uniforme.
        registro = {
            nombre: float(valor)
            for nombre, valor in zip(NOMBRES_CAMPOS, fila)
        }

        # Se agrega el registro preparado a la lista.
        registros.append(registro)

    # Se genera una copia de las etiquetas originales,
    # correspondientes a las especies del dataset Iris.
    etiquetas = dataset.target.copy()


    # ========================================================
    # 4. SIMULACIÓN CONTROLADA DE ERRORES
    # ========================================================

    # En caso de seleccionar el escenario inválido, se
    # modifican intencionalmente tres valores del primer
    # registro para comprobar que la etapa de validación
    # identifique los errores presentes en los datos.

    if escenario == "invalido":

        # Se simula un dato faltante.
        registros[0]["sepal_length"] = None

        # Se asigna un tipo de dato incorrecto en un campo
        # que debe contener un valor numérico.
        registros[0]["sepal_width"] = "abc"

        # Se asigna un valor negativo para simular un dato
        # fuera del rango permitido.
        registros[0]["petal_length"] = -2.0


    # ========================================================
    # 5. RESUMEN DE PREPARACIÓN
    # ========================================================

    # Se presenta en consola un resumen del proceso de
    # preparación para facilitar la revisión de los datos.

    print("\n" + "=" * 60)
    print("PREPARACIÓN DEL DATASET IRIS")
    print("=" * 60)

    # Se muestra el escenario seleccionado, la cantidad
    # de registros, etiquetas y características del dataset.
    print(f"Escenario: {escenario.upper()}")
    print(f"Total de registros: {len(registros)}")
    print(f"Total de etiquetas: {len(etiquetas)}")
    print(f"Características: {len(NOMBRES_CAMPOS)}")

    # Si el escenario es inválido, se informa que se realizó
    # la simulación controlada de errores.
    if escenario == "invalido":
        print("Simulación controlada de errores aplicada.")

    print("Preparación de datos finalizada.")

    # Finalmente, se retornan los registros y las etiquetas
    # para continuar con la etapa de validación del pipeline.
    return registros, etiquetas


# ============================================================
# 6. EJECUCIÓN INDEPENDIENTE DEL MÓDULO
# ============================================================

# Se habilita la ejecución independiente del módulo para
# comprobar su funcionamiento sin ejecutar todo el pipeline.

if __name__ == "__main__":

    # Se configura la recepción de argumentos desde la terminal.
    parser = argparse.ArgumentParser(
        description="Preparación del dataset Iris."
    )

    # Se establecen los escenarios disponibles para la ejecución,
    # dejando el escenario válido como opción predeterminada.
    parser.add_argument(
        "--escenario",
        choices=["valido", "invalido"],
        default="valido",
        help="Escenario de preparación de datos."
    )

    # Se obtiene el argumento ingresado desde la terminal.
    args = parser.parse_args()

    # Se ejecuta la preparación de los datos teniendo en cuenta
    # el escenario seleccionado.
    registros, etiquetas = preparar_datos(args.escenario)

    # Finalmente, se muestra el primer registro preparado
    # con el propósito de verificar la estructura de los datos
    # y los cambios realizados según el escenario seleccionado.
    print("\nPrimer registro preparado:")
    print(registros[0])