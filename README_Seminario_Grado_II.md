# Seminario de Grado II — Pipeline reproducible y control de calidad de datos

**Proyecto:** Estandarización de Pipelines y Control de Calidad de Datos  
**Caso de estudio:** Clasificación de especies de flores Iris con Random Forest  
**Tecnologías principales:** Python, scikit-learn, MLflow y pytest

## 1. Descripción y propósito

Este repositorio parte de la **Actividad 1.1: Implementación de Línea Base Reproducible y Trazabilidad de Experimentos** y la amplía con un pipeline que valida los datos según un contrato JSON **antes** de entrenar un modelo de clasificación.

El modelo utiliza cuatro características medidas en centímetros: longitud y ancho del sépalo, y longitud y ancho del pétalo. Su objetivo es predecir una de las tres especies de Iris incluidas en el conjunto de datos de `scikit-learn`.

**Objetivos:**

- Reproducir una línea base y comparar configuraciones de Random Forest con seguimiento en MLflow.
- Comprobar tipos, valores obligatorios, valores nulos y rangos de entrada mediante Python, sin bibliotecas externas para las reglas de validación.
- Definir un contrato de datos en formato JSON con ejemplos válidos e inválidos.
- Automatizar validación y entrenamiento con un único comando.
- Verificar con pruebas automatizadas tanto la aceptación de datos correctos como el bloqueo del entrenamiento ante datos inválidos.

## 2. Organización del proyecto

```text
Actividad_1_1_MLFlow/
├── .gitignore               # Archivos y carpetas excluidos de Git
├── data_contract.json       # Reglas y ejemplos del contrato de datos
├── readme.md                # Documentación del proyecto
├── requirements.txt         # Dependencias de Python
├── run_pipeline.py          # Carga, validación y orquestación
├── test_pipeline.py         # Cinco pruebas automatizadas
├── train.py                 # Entrenamiento Random Forest y seguimiento MLflow
└── validate_data.py         # Funciones de validación del contrato
```

**Archivos locales excluidos del repositorio:** `venv/`, `__pycache__/`, `.pytest_cache/`, `mlflow.db`, `mlruns/` y copias de seguridad. Estos pueden generarse durante la ejecución y no deben confundirse con los archivos fuente de la entrega. El historial local de MLflow no se publica automáticamente en GitHub.

## 3. Requisitos del entorno

- Python 3.10 o superior **compatible con las dependencias instaladas**. Entorno utilizado para las pruebas: **Python 3.13.14**.
- Visual Studio Code y, opcionalmente, su extensión de Python.
- Git para gestionar versiones y publicar en GitHub.

**Versiones verificadas en el entorno de desarrollo:**

| Dependencia | Versión utilizada |
|---|---:|
| MLflow | 3.17.2 |
| scikit-learn | 1.9.1 |
| pytest | 9.2.0 |

El archivo `requirements.txt` enumera las dependencias directas (`mlflow`, `scikit-learn`, `pytest`). Al no fijar versiones exactas, instalarlo en otra fecha podría seleccionar versiones distintas; para reproducir exactamente este entorno, se recomienda fijar las versiones anteriores después de comprobar la compatibilidad del entorno de destino.

## 4. Instalación desde cero en Windows (PowerShell)

Abrir la carpeta del repositorio en Visual Studio Code y ejecutar los siguientes comandos desde su raíz.

**Crear el entorno virtual:**

```powershell
python -m venv venv
```

**Activarlo:**

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell impide ejecutar el script de activación, habilitarlo **solo para la sesión actual** y volver a activarlo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

**Instalar las dependencias:**

```powershell
python -m pip install -r requirements.txt
```

Cuando la activación es correcta, la terminal muestra `(venv)`.

## 5. Ejecutar el pipeline completo — actividad de automatización

Con el entorno activo, ejecutar **un único comando**:

```powershell
python run_pipeline.py
```

El proceso realiza las siguientes etapas:

1. Carga las **150 muestras** del conjunto Iris y su etiqueta de especie.
2. Convierte sus cuatro características a registros con los nombres definidos en el contrato.
3. Carga `data_contract.json` y verifica cada registro mediante `validate_data.py`.
4. **Si existe algún registro inválido, se detiene antes del entrenamiento.**
5. Si todas las muestras son válidas, crea `X` a partir de esos **mismos registros previamente validados**, conserva sus etiquetas `y` y llama a `entrenar_modelo(X, y)` en `train.py`.
6. Divide el conjunto en entrenamiento/prueba (80 % / 20 %, `random_state=42`), entrena Random Forest y registra parámetros, métrica y modelo en MLflow.

### Resultado observado en la ejecución verificada

```text
Total de registros: 150
Registros válidos: 150
Registros inválidos: 0
VALIDACIÓN EXITOSA
Total de muestras: 150
Características por muestra: 4
Modelo registrado con accuracy: 1.0
Run ID: ffcf2d214bfd433a96db6d261746c879
PIPELINE EJECUTADO CORRECTAMENTE
```

**Interpretación:** `accuracy = 1.0` corresponde al **100 % de aciertos en las 30 muestras del conjunto de prueba de esta ejecución**; no demuestra precisión perfecta para todos los datos futuros. El Run ID identifica **esta ejecución local** de MLflow; no es un identificador universal reproducible en otra instalación.

## 6. Contrato JSON y validación de calidad

El archivo `data_contract.json` define las reglas para las cuatro variables de entrada:

- `sepal_length`: longitud del sépalo.
- `sepal_width`: ancho del sépalo.
- `petal_length`: longitud del pétalo.
- `petal_width`: ancho del pétalo.

Las reglas del ejercicio establecen valores numéricos, obligatorios y no nulos; prohíben valores no finitos y verifican los límites inferior y superior establecidos en el contrato (en la versión implementada, **0.1 y 10.0 cm**). Estos límites son **reglas operativas del ejercicio**, no una afirmación de límites botánicos universales.

Ejemplo válido:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

Ejemplo inválido para probar las restricciones:

```json
{
  "sepal_length": null,
  "sepal_width": "abc",
  "petal_length": -2.0,
  "petal_width": 0.2
}
```

La validación se implementa con funciones de Python y módulos de su biblioteca estándar, **sin Great Expectations ni otra biblioteca externa para evaluar las reglas**. El contrato es una descripción estructurada de los requisitos de entrada para el caso Iris; **no sustituye por sí mismo un servicio de inferencia desplegado**.

Para probar directamente los ejemplos del contrato:

```powershell
python validate_data.py
```

## 7. Pruebas automatizadas de calidad

El archivo `test_pipeline.py` define cinco pruebas compatibles con `unittest` y ejecutables también mediante `pytest`:

| Prueba | Objetivo |
|---|---|
| `test_01_datos_validos` | Aceptar una entrada conforme al contrato |
| `test_02_valores_nulos` | Rechazar un campo nulo |
| `test_03_tipos_incorrectos` | Rechazar una cadena de texto donde se exige un número |
| `test_04_rangos_invalidos` | Rechazar una medida fuera del rango permitido |
| `test_05_bloqueo_entrenamiento` | Simular una muestra inválida y verificar que no se invoque la función de entrenamiento |

Ejecutar las cinco pruebas mediante:

```powershell
python -m pytest -v test_pipeline.py
```

Alternativamente, usando únicamente el ejecutor de la biblioteca estándar:

```powershell
python -m unittest -v test_pipeline.py
```

**Resultado observado:** `5 passed, 1 warning` en pytest 9.2.0. La advertencia observada fue una notificación de obsolescencia de SQLAlchemy emitida desde MLflow y **no impidió superar los cinco casos**. El bloqueo de entrenamiento se verifica con una **simulación controlada**; esa prueba no equivale a una validación de todas las posibles situaciones de producción.

## 8. Actividad 1.1 — línea base y comparación histórica de experimentos

En el laboratorio inicial del profesor se propusieron cuatro configuraciones de Random Forest:

| Ejecución de referencia | `n_estimators` | `max_depth` |
|---|---:|---:|
| Baseline | 100 | `None` |
| Run 1 | 50 | 3 |
| Run 2 | 150 | 5 |
| Run 3 | 200 | 10 |

El procedimiento original consistió en ajustar los hiperparámetros en `train.py`, ejecutar `python train.py` después de cada cambio y comparar las corridas en MLflow.

**Distinción importante:** la versión actual de `train.py` usa `run_name="Run_4"`, **350 árboles** y `max_depth=10`; es una configuración adicional y **no reemplaza** las cuatro configuraciones históricas del laboratorio. Ejecutar `python train.py` directamente todavía permite entrenar de forma independiente, pero para esta actividad de calidad **la ruta recomendada es `python run_pipeline.py`**, pues incorpora la validación previa. Para repetir exactamente las cuatro configuraciones de referencia, es necesario establecer en el código los parámetros de cada experimento y ejecutar cada corrida por separado, o recuperar las corridas ya registradas en el entorno original.

## 9. Consultar las ejecuciones en MLflow

Abrir **otra terminal** desde la carpeta del proyecto, activar el entorno si hace falta e iniciar la interfaz:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Abrir en el navegador: <http://127.0.0.1:5000>

Seleccionar el experimento **`Proyecto_Final_Grado`** para visualizar los parámetros (`n_estimators`, `max_depth`), la métrica `accuracy` y los artefactos del modelo registrados. El contenido visible depende de las corridas presentes en el archivo **local** `mlflow.db` y de sus artefactos asociados.

**Nota:** MLflow puede mostrar advertencias sobre Git cuando el ejecutable no es accesible desde `PATH`; estas advertencias no significan necesariamente que el entrenamiento haya fallado. Para una evaluación real del estado del pipeline, verificar el resumen final y el Run ID.

## 10. Versionamiento y entrega

Git realiza el seguimiento de los archivos fuente y el README, mientras `.gitignore` evita publicar el entorno virtual, las cachés y los resultados locales que no forman parte del código fuente. Antes de cada publicación, revisar:

```powershell
git status
```

La carpeta del repositorio y la carpeta compartida de evidencias son **entregables complementarios**. La documentación y las capturas deberían permitir comprobar:

- Ejecución del pipeline completo con 150 registros válidos.
- Ejecución de las cinco pruebas automatizadas.
- Comparación de experimentos en MLflow, en la medida en que estén disponibles los resultados locales.
- Contrato JSON y casos de entrada válidos e inválidos.
- Enlace al repositorio GitHub y a la carpeta compartida, según las indicaciones de la guía evaluable.

El documento académico de entrega se elabora por separado con la presentación solicitada por la institución, el nombre de la actividad y el enlace compartido correspondiente.

## 11. Alcance y limitaciones

- El conjunto Iris se obtiene de `scikit-learn`; no se requiere descargar un CSV externo.
- Las validaciones comprueban la estructura y los rangos definidos por el contrato, pero no certifican la calidad de cualquier fuente futura.
- Las etiquetas `y` provienen del conjunto Iris y se comprueba su correspondencia en cantidad con los registros; el contrato documentado se centra en las **cuatro variables de entrada**.
- El pipeline es una ejecución local reproducible; no incluye despliegue de API ni monitorización continua.

