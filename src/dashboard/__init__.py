###Code for Dashboard development###

## Navigate to the desired project copy location##
cd [path]

## File Creation ##
$files = @(
    "README.md", "LICENSE", ".gitignore", ".python-version",
    "src\__init__.py",
    "src\data_pipeline\__init__.py", "src\data_pipeline\extract.py", "src\data_pipeline\transform.py", "src\data_pipeline\load.py",
    "src\analysis\__init__.py", "src\analysis\exploratory.py", "src\analysis\statistical.py",
    "src\modeling\__init__.py", "src\modeling\train.py", "src\modeling\predict.py", "src\modeling\evaluate.py",
    "src\dashboard\__init__.py", "src\dashboard\app.py", "src\dashboard\components.py",
    "tests\__init__.py", "tests\test_data_pipeline.py", "tests\test_analysis.py", "tests\test_modeling.py",
    "notebooks\01_data_exploration.ipynb", "notebooks\02_eda_analysis.ipynb", "notebooks\03_modeling_experiments.ipynb", "notebooks\04_dashboard_prototyping.ipynb",
    "docs\setup.md", "docs\data_dictionary.md", "docs\api_reference.md", "docs\deployment.md",
    "config\database.yaml", "config\model_params.yaml", "config\app_config.yaml",
    "scripts\setup_database.py", "scripts\run_pipeline.py", "scripts\deploy.py",
    "docker\Dockerfile", "docker\docker-compose.yml", "docker\requirements.txt"
)
foreach ($f in $files) { New-Item -ItemType File -Path $f -Force }

##Push to Git##
git add .
git commit -m "Implementing repository structure"
git push

####
