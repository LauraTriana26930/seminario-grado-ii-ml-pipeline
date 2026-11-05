# Actividad 1.1 – Implementación de Línea Base Reproducible y Trazabilidad de Experimentos

## Objetivo
Implementar una línea base (Baseline) utilizando un modelo de Machine Learning con el conjunto de datos Iris, 
registrando cada experimento mediante MLflow para garantizar la reproducibilidad, trazabilidad y comparación de resultados.
---

# Requisitos
Antes de iniciar, verificar que se encuentre instalado:
- Python 3.10 o superior
- Visual Studio Code
- Extensión de Python para VS Code
- Git (Opcional)
---

# 1. Crear la carpeta del proyecto
Crear una carpeta para el laboratorio.
```
Actividad_1_1_MLflow
```
- Abrir dicha carpeta desde Visual Studio Code.
---

# 2. Crear el entorno virtual
Abrir una terminal en VS Code.
- Ejecutar:
python -m venv venv
---

# 3. Activar el entorno virtual
- En Windows PowerShell ejecutar:
venv\Scripts\activate

Si PowerShell bloquea la ejecución de scripts, ejecutar primero:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Luego volver a activar el entorno:
```powershell
venv\Scripts\activate
```
Cuando el entorno esté activo deberá aparecer:
```
(venv)
```
al inicio de la línea de comandos.
---

# 4. Instalar las dependencias
- Crear el archivo:
```
requirements.txt
```
- con el siguiente contenido:
```text
mlflow
scikit-learn
```
- Instalar las librerías:

```powershell
pip install -r requirements.txt
```
---

# 5. Crear el archivo train.py
- Crear el archivo:
```
train.py
```
- Copiar el código fuente proporcionado para el laboratorio.
---

# 6. Ejecutar el Baseline

- Desde la terminal ejecutar:

```powershell
python train.py
```
- Si el entrenamiento fue exitoso aparecerá un resultado similar a:
```
Modelo registrado con accuracy: 1.0
Run ID:
xxxxxxxxxxxxxxxxxxxxxxxx
```
---

# 7. Abrir MLflow UI
- Abrir una **segunda terminal** en Visual Studio Code.

- Activar nuevamente el entorno virtual (de ser necesario):

```powershell
venv\Scripts\activate
```

- Ejecutar:
```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

- Abrir el navegador en:
```
http://127.0.0.1:5000
```
---

# 8. Ejecutar nuevos experimentos

- Modificar en el archivo `train.py` los hiperparámetros del modelo.

- baseline:
with mlflow.start_run(run_name="Baseline"):
    n_estimators = 100
    max_depth = None  

## 3 runs adicionales.

- Run 1:
with mlflow.start_run(run_name="Run_1_n50_depth3"):
    n_estimators = 50
    max_depth = 3

python train.py

- Run 2:
with mlflow.start_run(run_name="Run_2_n150_depth5"):
    n_estimators = 150
    max_depth = 5

- Run 3:
with mlflow.start_run(run_name="Run_3_n200_depth10"):
    n_estimators = 200
    max_depth = 10

- Para cada uno de los Run, guardar los cambios.
- Ejecutar nuevamente:
```powershell
python train.py
```


| Run      | n_estimators | max_depth |
|----------|-------------:|----------:|
| Baseline | 100          | None      |
| Run 1    | 50           | 3         |
| Run 2    | 150          | 5         |
| Run 3    | 200          | 10        |

---

# 9. Comparar experimentos

- Luego de recargar MLflow UI. podemos ver 4 runs:
Baseline
Run_1_n50_depth3
Run_2_n150_depth5
Run_3_n200_depth10


- Ingresar nuevamente a MLflow UI.

- Seleccionar:
```
Proyecto_Final_Grado
```
Comparar:
- Accuracy
- Parámetros
- Modelos registrados
Tomar las capturas de pantalla requeridas para el informe.
---

# Estructura del proyecto


Actividad_1_1_MLflow
│
├── train.py
├── requirements.txt
├── mlflow.db
├── README.md
├── venv/
└── mlruns/


---

# Resultado esperado

Al finalizar el laboratorio se deberá contar con:

- Un experimento Baseline.
- Tres experimentos adicionales.
- Cuatro ejecuciones registradas en MLflow.
- Comparación de métricas.
- Modelo almacenado en MLflow.
- Evidencia de reproducibilidad y trazabilidad de experimentos.