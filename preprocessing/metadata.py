import yaml
from pathlib import Path


# Project root (company-chatbot)
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = BASE_DIR / "config" / "role_mapping.yaml"


def load_role_mapping(config_path: str = None) -> dict:
    path = Path(config_path) if config_path else CONFIG_PATH

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def infer_department(file_path: str, role_config: dict) -> str:
    file_path = file_path.replace("\\", "/").lower()

    for department, config in role_config["roles"].items():
        for folder in config["folders"]:
            if folder.lower() in file_path:
                return department

    return "Unknown"


def get_allowed_roles(department: str, role_config: dict) -> list:
    return role_config["roles"].get(department, {}).get("allowed_roles", [])
