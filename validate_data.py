
# ============================================================
# SEMINARIO DE GRADO II
# ESPECIALIZACIÓN EN CIENCIA DE DATOS
# ============================================================
# Proyecto: Estandarización de Pipelines y Control de Calidad
#           de Datos
# Archivo: validate_data.py
#
# Objetivo:
# Validar los datos de entrada del modelo Iris, verificando
# tipos de datos, valores nulos y rangos permitidos según
# las reglas definidas en data_contract.json.
#
# Se utilizan únicamente librerías estándar de Python.
# ============================================================


# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

import json
import math
from pathlib import Path


# ============================================================
# 2. CARGA DEL CONTRATO DE DATOS
# ============================================================

def cargar_contrato():
    """Carga las reglas de validación desde el archivo JSON."""

    ruta = Path(__file__).resolve().parent / "data_contract.json"

    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# ============================================================
# 3. VALIDACIÓN DE DATOS DE ENTRADA
# ============================================================

def validar_entrada(datos, contrato):
    """
    Comprueba que una entrada cumpla el contrato de datos.

    Verifica:
    - Presencia de campos obligatorios.
    - Ausencia de valores nulos.
    - Tipos de datos numéricos.
    - Rangos mínimos y máximos.
    """

    errores = []
    campos = contrato["input_features"]

    # Validar que la entrada sea un objeto.
    if not isinstance(datos, dict):
        return False, ["La entrada debe ser un objeto JSON."]

    for nombre, reglas in campos.items():

        # 3.1. Verificación de campos obligatorios
        if nombre not in datos:
            if reglas.get("required", False):
                errores.append(f"Falta el campo obligatorio: {nombre}")
            continue

        valor = datos[nombre]

        # 3.2. Verificación de valores nulos
        if valor is None:
            if not reglas.get("nullable", True):
                errores.append(f"{nombre}: no permite valores nulos.")
            continue

        # 3.3. Verificación de tipos de datos
        if reglas.get("type") == "number":

            if isinstance(valor, bool) or not isinstance(
                valor, (int, float)
            ):
                errores.append(
                    f"{nombre}: debe ser un valor numérico."
                )
                continue

            if not math.isfinite(valor):
                errores.append(
                    f"{nombre}: debe ser un número finito."
                )
                continue

        # 3.4. Verificación de rangos permitidos
        minimo = reglas.get("min")
        maximo = reglas.get("max")

        if minimo is not None and valor < minimo:
            errores.append(
                f"{nombre}: valor {valor} inferior al mínimo {minimo}."
            )

        if maximo is not None and valor > maximo:
            errores.append(
                f"{nombre}: valor {valor} superior al máximo {maximo}."
            )

    # Verificar campos adicionales no definidos.
    for nombre in datos:
        if nombre not in campos:
            errores.append(
                f"Campo no permitido en el contrato: {nombre}"
            )

    return len(errores) == 0, errores


# ============================================================
# 4. EJECUCIÓN DE PRUEBAS DE VALIDACIÓN
# ============================================================

def ejecutar_pruebas():

    contrato = cargar_contrato()

    ejemplos = {
        "ENTRADA VÁLIDA": contrato["valid_example"],
        "ENTRADA INVÁLIDA": contrato["invalid_example"]
    }

    print("\n" + "=" * 60)
    print("VALIDACIÓN DE CALIDAD DE DATOS - DATASET IRIS")
    print("=" * 60)

    for nombre, datos in ejemplos.items():

        valido, errores = validar_entrada(datos, contrato)

        print(f"\nPrueba: {nombre}")

        if valido:
            print("RESULTADO: VALIDACIÓN EXITOSA")
        else:
            print("RESULTADO: VALIDACIÓN RECHAZADA")

            for error in errores:
                print(f" - {error}")

    print("\n" + "=" * 60)
    print("PRUEBAS DE VALIDACIÓN FINALIZADAS")
    print("=" * 60)


# ============================================================
# 5. PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":
    ejecutar_pruebas()
