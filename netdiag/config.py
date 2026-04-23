import json
from netdiag.models import AppConfig

def load_config(path="targets.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig.model_validate(data)