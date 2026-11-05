
# ==========================================================================================
# SEMINARIO DE GRADO II
# ESPECIALIZACIÓN EN CIENCIA DE DATOS
# ==========================================================================================
# Proyecto: Estandarización de Pipelines y Control de Calidad de Datos
#
# Objetivo:
# Entrenar y evaluar un modelo Random Forest utilizando datos previamente
# validados, registrando hiperparámetros, métricas y modelo mediante MLflow.
#
# El archivo permite:
# 1. Recibir datos validados desde run_pipeline.py.
# 2. Ejecutarse de manera independiente para reproducir el entrenamiento.
# ==========================================================================================


# ==========================================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================================================================

import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# ==========================================================================================
# 2. CONFIGURACIÓN DE MLFLOW
# ==========================================================================================

# Configurar SQLite como almacenamiento local de experimentos.
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Nombre del experimento donde se registrarán los resultados.
mlflow.set_experiment("Proyecto_Final_Grado")


# ==========================================================================================
# 3. FUNCIÓN DE ENTRENAMIENTO
# ==========================================================================================

def entrenar_modelo(X, y):
    """
    Entrena y evalúa un modelo Random Forest utilizando
    las características (X) y etiquetas (y) recibidas.

    Esta función permite que run_pipeline.py entregue
    directamente los datos que superaron la validación.
    """

    # ======================================================================================
    # 3.1. INICIO DEL EXPERIMENTO
    # ======================================================================================

    with mlflow.start_run(run_name="Run_4"):

        # ==================================================================================
        # 3.2. DEFINICIÓN DE HIPERPARÁMETROS
        # ==================================================================================

        n_estimators = 350  # Número de árboles del Random Forest.
        max_depth = 10     # Profundidad máxima de cada árbol.

        # ==================================================================================
        # 3.3. REGISTRO DE HIPERPARÁMETROS EN MLFLOW
        # ==================================================================================

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        # ==================================================================================
        # 3.4. DIVISIÓN DE DATOS EN ENTRENAMIENTO Y PRUEBA
        # ==================================================================================

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # ==================================================================================
        # 3.5. CONSTRUCCIÓN DEL MODELO RANDOM FOREST
        # ==================================================================================

        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )

        # ==================================================================================
        # 3.6. ENTRENAMIENTO DEL MODELO
        # ==================================================================================

        model.fit(X_train, y_train)

        # ==================================================================================
        # 3.7. EVALUACIÓN DEL MODELO
        # ==================================================================================

        accuracy = model.score(X_test, y_test)

        # ==================================================================================
        # 3.8. REGISTRO DE MÉTRICAS Y MODELO EN MLFLOW
        # ==================================================================================

        mlflow.log_metric("accuracy", accuracy)

        # Guardar el modelo mediante MLflow, conservando
        # la configuración utilizada en el código original.
        mlflow.sklearn.log_model(
            model,
            name="iris_model",
            skops_trusted_types=["sklearn.tree._tree.Tree"]
        )

        # ==================================================================================
        # 3.9. PRESENTACIÓN DE RESULTADOS
        # ==================================================================================

        print(f"Modelo registrado con accuracy: {accuracy}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")

        return model, accuracy


# ==========================================================================================
# 4. EJECUCIÓN INDEPENDIENTE DEL ARCHIVO
# ==========================================================================================

if __name__ == "__main__":

    # Esta carga de Iris se utiliza únicamente cuando
    # train.py se ejecuta directamente desde la terminal.
    data = load_iris()

    X = data.data
    y = data.target

    entrenar_modelo(X, y)
