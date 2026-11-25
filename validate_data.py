# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

import json
import math
import argparse

from pathlib import Path
from numbers import Integral


# ============================================================
# 2. CARGA DEL CONTRATO DE DATOS
# ============================================================

def cargar_contrato():
    """Carga el contrato de datos desde el archivo JSON."""

    ruta = Path(__file__).resolve().parent / "data_contract.json"

    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# ============================================================
# 3. VALIDACIÓN INDIVIDUAL DE REGISTROS
# ============================================================

def validar_entrada(datos, contrato):
    """
    Valida un registro según las reglas del contrato.

    Retorna:
    - Estado de validación.
    - Lista de errores identificados.
    """

    errores = []

    campos = contrato["input_features"]
    reglas_dataset = contrato["dataset_rules"]

    # 3.1. Validar estructura del registro.

    if not isinstance(datos, dict):

        return False, [
            "La entrada debe ser un objeto JSON."
        ]

    # 3.2. Validar cantidad de características.

    cantidad_esperada = reglas_dataset["expected_features"]

    if len(datos) != cantidad_esperada:

        errores.append(
            f"Se esperaban {cantidad_esperada} características "
            f"y se recibieron {len(datos)}."
        )

    # 3.3. Validar las características del contrato.

    for nombre, reglas in campos.items():

        # Campos obligatorios.

        if nombre not in datos:

            if reglas.get("required", False):

                errores.append(
                    f"Falta el campo obligatorio: {nombre}"
                )

            continue

        valor = datos[nombre]

        # Valores nulos.

        if valor is None:

            if not reglas.get("nullable", True):

                errores.append(
                    f"{nombre}: no permite valores nulos."
                )

            continue

        # Tipos de datos numéricos.

        if reglas.get("type") == "number":

            if (
                isinstance(valor, bool)
                and not reglas.get("allow_boolean", False)
            ):

                errores.append(
                    f"{nombre}: no permite valores booleanos."
                )

                continue

            if not isinstance(valor, (int, float)):

                errores.append(
                    f"{nombre}: debe ser un valor numérico."
                )

                continue

            # Valores finitos: rechazo de NaN e infinitos.

            if reglas.get("finite", True):

                if not math.isfinite(valor):

                    errores.append(
                        f"{nombre}: debe ser un número finito."
                    )

                    continue

        # Rangos permitidos.

        minimo = reglas.get("min")
        maximo = reglas.get("max")

        if minimo is not None and valor < minimo:

            errores.append(
                f"{nombre}: valor {valor} inferior "
                f"al mínimo {minimo}."
            )

        if maximo is not None and valor > maximo:

            errores.append(
                f"{nombre}: valor {valor} superior "
                f"al máximo {maximo}."
            )

    # 3.4. Validar campos adicionales.

    if not reglas_dataset.get("allow_extra_fields", False):

        for nombre in datos:

            if nombre not in campos:

                errores.append(
                    f"Campo no permitido en el contrato: {nombre}"
                )

    return len(errores) == 0, errores


# ============================================================
# 4. VALIDACIÓN DE ETIQUETAS
# ============================================================

def validar_etiqueta(etiqueta, contrato):
    """
    Verifica que la etiqueta corresponda a una clase
    permitida del dataset Iris.
    """

    reglas = contrato["target"]

    if etiqueta is None:

        if not reglas.get("nullable", True):

            return False, "La etiqueta no permite valores nulos."

        return True, None

    if reglas.get("type") == "integer":

        if (
            isinstance(etiqueta, bool)
            or not isinstance(etiqueta, Integral)
        ):

            return False, "La etiqueta debe ser un número entero."

    if etiqueta not in reglas["allowed_values"]:

        return False, (
            f"Etiqueta {etiqueta} fuera de las clases permitidas."
        )

    return True, None


# ============================================================
# 5. VALIDACIÓN INTEGRAL DEL DATASET
# ============================================================

def validar_dataset(registros, etiquetas, contrato):
    """
    Valida la estructura general, las características
    y las etiquetas del dataset.

    Genera un reporte estructurado de calidad.
    """

    reglas = contrato["dataset_rules"]

    total_registros = len(registros)

    registros_validos = 0
    registros_invalidos = 0
    etiquetas_invalidas = 0

    errores_dataset = []
    detalle_errores = []

    # 5.1. Verificar que el dataset no esté vacío.

    if not reglas.get("allow_empty", False):

        if total_registros == 0:

            errores_dataset.append(
                "El dataset no puede estar vacío."
            )

    # 5.2. Verificar correspondencia entre registros y etiquetas.

    if reglas.get("require_target_alignment", True):

        if len(registros) != len(etiquetas):

            errores_dataset.append(
                "La cantidad de registros y etiquetas no coincide."
            )

    # 5.3. Validar individualmente los registros.

    for numero, registro in enumerate(registros, start=1):

        valido, errores = validar_entrada(
            registro,
            contrato
        )

        if valido:

            registros_validos += 1

        else:

            registros_invalidos += 1

            detalle_errores.append({
                "registro": numero,
                "errores": errores
            })

    # 5.4. Validar individualmente las etiquetas.

    for numero, etiqueta in enumerate(etiquetas, start=1):

        valido, error = validar_etiqueta(
            etiqueta,
            contrato
        )

        if not valido:

            etiquetas_invalidas += 1

            errores_dataset.append(
                f"Etiqueta {numero}: {error}"
            )

    # 5.5. Calcular el porcentaje de calidad de registros.

    porcentaje_calidad = (
        registros_validos / total_registros * 100
        if total_registros > 0
        else 0.0
    )

    # 5.6. Determinar el estado general de validación.

    aprobado = (
        registros_invalidos == 0
        and etiquetas_invalidas == 0
        and len(errores_dataset) == 0
    )

    # 5.7. Construir el reporte de calidad.

    reporte = {
        "version_contrato": contrato["version"],
        "total_registros": total_registros,
        "total_etiquetas": len(etiquetas),
        "registros_validos": registros_validos,
        "registros_invalidos": registros_invalidos,
        "etiquetas_invalidas": etiquetas_invalidas,
        "porcentaje_calidad": round(porcentaje_calidad, 2),
        "total_errores": (
            sum(
                len(item["errores"])
                for item in detalle_errores
            )
            + len(errores_dataset)
        ),
        "aprobado": aprobado,
        "errores_dataset": errores_dataset,
        "detalle_errores": detalle_errores
    }

    return reporte


# ============================================================
# 6. PRESENTACIÓN DEL REPORTE DE CALIDAD
# ============================================================

def mostrar_reporte(reporte):
    """Presenta los resultados de validación en la terminal."""

    print("\n" + "=" * 60)
    print("REPORTE DE CONTROL DE CALIDAD")
    print("=" * 60)

    print(f"Versión del contrato: {reporte['version_contrato']}")
    print(f"Total de registros: {reporte['total_registros']}")
    print(f"Total de etiquetas: {reporte['total_etiquetas']}")
    print(f"Registros válidos: {reporte['registros_validos']}")
    print(f"Registros inválidos: {reporte['registros_invalidos']}")
    print(f"Etiquetas inválidas: {reporte['etiquetas_invalidas']}")
    print(f"Calidad de registros: {reporte['porcentaje_calidad']} %")
    print(f"Total de errores: {reporte['total_errores']}")

    # Mostrar errores generales del dataset.

    for error in reporte["errores_dataset"]:

        print(f"\nERROR GENERAL: {error}")

    # Mostrar errores individuales.

    for item in reporte["detalle_errores"]:

        print(f"\nRegistro {item['registro']}: RECHAZADO")

        for error in item["errores"]:

            print(f" - {error}")

    print("\n" + "-" * 60)

    if reporte["aprobado"]:

        print("ESTADO: VALIDACIÓN APROBADA")

    else:

        print("ESTADO: VALIDACIÓN RECHAZADA")
        print("Los datos no cumplen el contrato de calidad.")

    print("=" * 60)


# ============================================================
# 7. EJECUCIÓN INDEPENDIENTE DEL VALIDADOR
# ============================================================

if __name__ == "__main__":

    from prepare import preparar_datos

    parser = argparse.ArgumentParser(
        description="Control de calidad del dataset Iris."
    )

    parser.add_argument(
        "--escenario",
        choices=["valido", "invalido"],
        default="valido"
    )

    args = parser.parse_args()

    contrato = cargar_contrato()

    registros, etiquetas = preparar_datos(
        args.escenario
    )

    reporte = validar_dataset(
        registros,
        etiquetas,
        contrato
    )

    mostrar_reporte(reporte)

    # Código de salida para la automatización de tareas.

    raise SystemExit(0 if reporte["aprobado"] else 1)