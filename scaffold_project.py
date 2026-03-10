import os

base_dir = r"d:\02_dicitionary\github\h4\algorithm_repository"

directories = [
    "alembic/versions",
    "app",
    "app/api/v1",
    "app/schemas",
    "app/models",
    "app/services",
    "app/engine",
    "app/algorithms/ts_preprocessing",
    "app/algorithms/ts_feature",
    "app/algorithms/ts_anomaly",
    "app/algorithms/text_nlp",
    "app/algorithms/cv_detection",
    "app/algorithms/cv_ocr",
    "app/core",
    "tests/test_api",
    "tests/test_services",
    "tests/test_engine",
    "tests/test_algorithms"
]

files = [
    "alembic/env.py",
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/api/__init__.py",
    "app/api/deps.py",
    "app/api/v1/__init__.py",
    "app/api/v1/router.py",
    "app/api/v1/algorithms.py",
    "app/api/v1/executions.py",
    "app/schemas/__init__.py",
    "app/schemas/algorithm.py",
    "app/schemas/execution.py",
    "app/schemas/flow_dsl.py",
    "app/schemas/callback.py",
    "app/models/__init__.py",
    "app/models/algorithm.py",
    "app/models/execution.py",
    "app/models/template.py",
    "app/services/__init__.py",
    "app/services/algorithm_service.py",
    "app/services/execution_service.py",
    "app/services/validation_service.py",
    "app/services/callback_service.py",
    "app/services/storage_service.py",
    "app/services/template_service.py",
    "app/engine/__init__.py",
    "app/engine/orchestrator.py",
    "app/engine/dag.py",
    "app/engine/tasks.py",
    "app/algorithms/__init__.py",
    "app/algorithms/base.py",
    "app/algorithms/registry.py",
    "app/algorithms/ts_preprocessing/__init__.py",
    "app/algorithms/ts_preprocessing/linear_interp.py",
    "app/algorithms/ts_preprocessing/ffill.py",
    "app/algorithms/ts_feature/__init__.py",
    "app/algorithms/ts_anomaly/__init__.py",
    "app/algorithms/text_nlp/__init__.py",
    "app/algorithms/cv_detection/__init__.py",
    "app/algorithms/cv_ocr/__init__.py",
    "app/core/__init__.py",
    "app/core/database.py",
    "app/core/redis.py",
    "app/core/minio_client.py",
    "app/core/celery_app.py",
    "app/core/security.py",
    "app/core/exceptions.py",
    "app/core/logging.py",
    "tests/conftest.py",
    "alembic.ini",
    "pyproject.toml",
    "docker-compose.yml",
    "Dockerfile",
    "README.md"
]

for d in directories:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

for f in files:
    file_path = os.path.join(base_dir, f)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as fs:
            pass

print("Project structure created successfully.")
