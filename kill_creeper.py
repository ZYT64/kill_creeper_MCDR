import json
import time
import os
from threading import Thread, Event

CONFIG_PATH = "config/kill_creeper/config.json"
DEFAULT_CONFIG = {
    "enabled": True,
    "distance": 10,
    "drop": False
}

stop_event = Event()
error_shown = False
config = {}

def load_config():
    global config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG.copy()
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

def on_load(server, prev_module):
    global stop_event, error_shown
    error_shown = False
    load_config()
    stop_event.clear()
    server.logger.info("Creeper killer loaded, edit config/kill_creeper/config.json to change settings")
    if config.get("enabled", True):
        Thread(target=kill_loop, args=(server,), daemon=True).start()

def on_unload(server):
    stop_event.set()

def kill_loop(server):
    global error_shown, config
    while not stop_event.is_set():
        load_config()
        if config.get("enabled", True):
            try:
                distance = config.get("distance", 10)
                drop = config.get("drop", False)
                if drop:
                    cmd = f'/execute at @a run kill @e[type=creeper, distance=..{distance}]'
                else:
                    cmd = f'/execute at @a run tp @e[type=creeper, distance=..{distance}] ~ -1000 ~'
                server.execute(cmd)
            except Exception as e:
                if not error_shown:
                    server.logger.error(f'Error executing kill command: {e}')
                    error_shown = True
        time.sleep(1)
