# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 2. CONFIGURACIÓN DEL MODELO
# ============================================================

N_ESTIMATORS = 350
MAX_DEPTH = 10
RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# 3. FUNCIÓN DE ENTRENAMIENTO
# ============================================================

def entrenar_modelo(X, y):
    """
    Entrena y evalúa Random Forest utilizando los datos
    que superaron el control de calidad.

    El registro en MLflow utiliza la ejecución activa
    gestionada por el automatizador de tareas.
    """

    # Verificar que exista una ejecución activa en MLflow.

    if mlflow.active_run() is None:

        raise RuntimeError(
            "No existe una ejecución activa en MLflow."
        )

    print("\n" + "=" * 60)
    print("ENTRENAMIENTO DEL MODELO RANDOM FOREST")
    print("=" * 60)


    # ========================================================
    # 3.1. DIVISIÓN DE LOS DATOS
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print(f"Muestras de entrenamiento: {len(X_train)}")
    print(f"Muestras de prueba: {len(X_test)}")


    # ========================================================
    # 3.2. REGISTRO DE HIPERPARÁMETROS
    # ========================================================

    mlflow.log_params({
        "algorithm": "RandomForestClassifier",
        "n_estimators": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "stratified_split": True,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    })


    # ========================================================
    # 3.3. CONSTRUCCIÓN DEL MODELO
    # ========================================================

    modelo = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE
    )


    # ========================================================
    # 3.4. ENTRENAMIENTO
    # ========================================================

    modelo.fit(X_train, y_train)

    print("Entrenamiento finalizado correctamente.")


    # ========================================================
    # 3.5. EVALUACIÓN DEL MODELO
    # ========================================================

    predicciones = modelo.predict(X_test)

    metricas = {

        "accuracy": accuracy_score(
            y_test,
            predicciones
        ),

        "precision_macro": precision_score(
            y_test,
            predicciones,
            average="macro",
            zero_division=0
        ),

        "recall_macro": recall_score(
            y_test,
            predicciones,
            average="macro",
            zero_division=0
        ),

        "f1_macro": f1_score(
            y_test,
            predicciones,
            average="macro",
            zero_division=0
        )
    }


    # ========================================================
    # 3.6. REGISTRO DE MÉTRICAS EN MLFLOW
    # ========================================================

    mlflow.log_metrics(metricas)


    # ========================================================
    # 3.7. REGISTRO DEL MODELO
    # ========================================================

    mlflow.sklearn.log_model(
        modelo,
        name="iris_model",
        skops_trusted_types=["sklearn.tree._tree.Tree"]
    )


    # ========================================================
    # 3.8. PRESENTACIÓN DE RESULTADOS
    # ========================================================

    print("\nRESULTADOS DE EVALUACIÓN")
    print("-" * 60)

    for nombre, valor in metricas.items():

        print(f"{nombre}: {valor:.4f}")

    print("\nModelo registrado correctamente en MLflow.")

    print(
        f"Run ID: {mlflow.active_run().info.run_id}"
    )

    return modelo, metricas


# ============================================================
# 4. EJECUCIÓN INDEPENDIENTE DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    from pathlib import Path

    from prepare import preparar_datos, NOMBRES_CAMPOS

    from validate_data import (
        cargar_contrato,
        validar_dataset,
        mostrar_reporte
    )

    # Preparar y validar los datos antes del entrenamiento.

    registros, etiquetas = preparar_datos("valido")

    contrato = cargar_contrato()

    reporte = validar_dataset(
        registros,
        etiquetas,
        contrato
    )

    mostrar_reporte(reporte)

    if not reporte["aprobado"]:

        print("\nENTRENAMIENTO BLOQUEADO")

        raise SystemExit(1)

    # Construir las características previamente validadas.

    X = [
        [registro[campo] for campo in NOMBRES_CAMPOS]
        for registro in registros
    ]

    y = etiquetas

    # Configurar el almacenamiento local de MLflow.

    ruta_db = (
        Path(__file__).resolve().parent / "mlflow.db"
    )

    mlflow.set_tracking_uri(
        f"sqlite:///{ruta_db.as_posix()}"
    )

    mlflow.set_experiment(
        "Actividad_2_1_Control_Calidad"
    )

    # Ejecución independiente para verificar el módulo.

    with mlflow.start_run(
        run_name="Prueba_Modulo_Entrenamiento"
    ):

        mlflow.set_tag("activity", "2.1")

        mlflow.set_tag(
            "execution_type",
            "module_test"
        )

        mlflow.set_tag(
            "contract_version",
            contrato["version"]
        )

        modelo, metricas = entrenar_modelo(X, y)