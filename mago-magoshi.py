#!/usr/bin/env python3
# ============================================================
# CASA CORE 6.1 — MAGO MAGOSHI EDITION (FIXED)
# ============================================================

import os, sys, json, time
from datetime import datetime
from urllib import request
import paho.mqtt.client as mqtt

VERSION = "6.1-MAGOSHI"

BASE = os.path.expanduser("~/.casacore")
DEVICES = os.path.join(BASE, "devices.json")
LOG = os.path.join(BASE, "casacore.log")

ASCII = r"""                                                               _     _ 
 _ __ ___   __ _  __ _  ___    _ __ ___   __ _  __ _  ___  ___| |__ (_)
| '_ ` _ \ / _` |/ _` |/ _ \  | '_ ` _ \ / _` |/ _` |/ _ \/ __| '_ \| |
| | | | | | (_| | (_| | (_) | | | | | | | (_| | (_| | (_) \__ \ | | | |
|_| |_| |_|\__,_|\__, |\___/  |_| |_| |_|\__,_|\__, |\___/|___/_| |_|_|
                 |___/                         |___/                   
        CASA CORE 6.1 — MAGO MAGOSHI
   “controle é poder, poder é silêncio”
"""

# ============================================================

def ensure_base():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(DEVICES):
        with open(DEVICES, "w") as f:
            json.dump({}, f)

def log(msg):
    ensure_base()
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def clear():
    os.system("clear" if os.name != "nt" else "cls")

# ============================================================
# DEVICE
# ============================================================

class Device:
    def __init__(self, name, mode, config):
        self.name = name
        self.mode = mode
        self.config = config

    def on(self):
        return self._send(True)

    def off(self):
        return self._send(False)

    def _send(self, state):
        if self.mode == "http":
            path = self.config["on"] if state else self.config["off"]
            url = f"http://{self.config['ip']}{path}"
            try:
                request.urlopen(url, timeout=3)
                log(f"{self.name} HTTP {'ON' if state else 'OFF'}")
                return True
            except Exception as e:
                log(f"{self.name} HTTP FAIL: {e}")
                return False

        elif self.mode == "mqtt":
            try:
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                client.connect(
                    self.config["broker"],
                    self.config.get("port", 1883),
                    60
                )
                payload = self.config["payload_on"] if state else self.config["payload_off"]
                client.publish(self.config["topic"], payload)
                client.disconnect()
                log(f"{self.name} MQTT {'ON' if state else 'OFF'}")
                return True
            except Exception as e:
                log(f"{self.name} MQTT FAIL: {e}")
                return False

# ============================================================
# CORE
# ============================================================

class CasaCore:
    def __init__(self):
        ensure_base()
        self.devices = {}
        self.load()

    def load(self):
        try:
            with open(DEVICES) as f:
                data = json.load(f)
            for name, d in data.items():
                self.devices[name] = Device(name, d["mode"], d["config"])
        except:
            self.devices = {}

    def save(self):
        data = {}
        for n, d in self.devices.items():
            data[n] = {"mode": d.mode, "config": d.config}
        with open(DEVICES, "w") as f:
            json.dump(data, f, indent=4)

    def add(self):
        clear()
        print(">>> MAGO MAGOSHI :: ADICIONAR DISPOSITIVO")
        name = input("Nome: ").strip()
        mode = input("Modo (http/mqtt): ").strip()

        if mode == "http":
            cfg = {
                "ip": input("IP: ").strip(),
                "on": input("Path ON: ").strip(),
                "off": input("Path OFF: ").strip()
            }

        elif mode == "mqtt":
            cfg = {
                "broker": input("Broker IP: ").strip(),
                "topic": input("Topic: ").strip(),
                "payload_on": input("Payload ON: ").strip(),
                "payload_off": input("Payload OFF: ").strip()
            }
        else:
            print("Modo inválido.")
            time.sleep(1)
            return

        self.devices[name] = Device(name, mode, cfg)
        self.save()
        log(f"Device criado por MAGO MAGOSHI: {name}")

    def list(self):
        clear()
        print(">>> DISPOSITIVOS — MAGO MAGOSHI\n")
        if not self.devices:
            print("Nenhum dispositivo.")
        for i, n in enumerate(self.devices, 1):
            print(f"{i}. {n} [{self.devices[n].mode}]")
        input("\nENTER")

    def control(self, state):
        if not self.devices:
            print("Nenhum dispositivo.")
            time.sleep(1)
            return

        clear()
        for i, n in enumerate(self.devices, 1):
            print(f"{i}. {n}")
        try:
            idx = int(input("Escolha: ")) - 1
            dev = list(self.devices.values())[idx]
            ok = dev.on() if state else dev.off()
            print("EXECUTADO" if ok else "FALHOU")
        except:
            print("Escolha inválida.")
        time.sleep(1)

# ============================================================

def main():
    core = CasaCore()
    while True:
        clear()
        print(ASCII)
        print("1 Listar dispositivos")
        print("2 Adicionar dispositivo")
        print("3 Ligar")
        print("4 Desligar")
        print("5 Sair")
        op = input(">> ")

        if op == "1": core.list()
        elif op == "2": core.add()
        elif op == "3": core.control(True)
        elif op == "4": core.control(False)
        elif op == "5": sys.exit()

if __name__ == "__main__":
    main()
