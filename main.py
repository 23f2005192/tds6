import os
import yaml
from dotenv import load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load .env
# -----------------------------
# Existing OS environment variables are NOT overwritten.
load_dotenv(override=False)

# -----------------------------
# Layer 1: Defaults
# -----------------------------
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# -----------------------------
# Layer 2: YAML
# -----------------------------
yaml_file = "config.development.yaml"

if os.path.exists(yaml_file):
    with open(yaml_file, "r") as f:
        yaml_config = yaml.safe_load(f) or {}
        config.update(yaml_config)

# -----------------------------
# Layer 3 & 4:
# .env + OS Environment
#
# os.getenv() automatically
# returns OS env first.
# -----------------------------
mapping = {
    "APP_PORT": "port",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
    "NUM_WORKERS": "workers",
}

for env_name, config_name in mapping.items():

    value = os.getenv(env_name)

    if value is not None:
        config[config_name] = value


def to_bool(value):
    return str(value).strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    final = dict(config)

    # -------------------------
    # Layer 5: CLI Overrides
    # -------------------------
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        final[key] = value

    # -------------------------
    # Type Coercion
    # -------------------------
    final["port"] = int(final["port"])

    final["workers"] = int(final["workers"])

    final["debug"] = to_bool(final["debug"])

    final["log_level"] = str(final["log_level"])

    # -------------------------
    # Secret Masking
    # -------------------------
    final["api_key"] = "****"

    return final


@app.get("/")
def root():
    return {"status": "running"}
