import os

BASE_URL = os.environ.get("SMARTWIFI_BASE_URL", "https://qa.datawifi.co/easyfi/web/app.php")
AUTH_STATE_PATH = os.environ.get("SMARTWIFI_AUTH_STATE", "auth_state.json")
