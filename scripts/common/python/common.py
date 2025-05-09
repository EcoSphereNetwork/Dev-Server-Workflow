"""
Gemeinsame Python-Bibliothek für das Dev-Server-Workflow-Projekt.

Diese Bibliothek enthält gemeinsame Funktionen und Klassen für alle Python-Skripte
im Dev-Server-Workflow-Projekt.
"""

import os
import sys
import json
import yaml
import logging
import subprocess
import argparse
import time
import signal
import socket
import platform
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Type, TypeVar, Generic
from pathlib import Path
from datetime import datetime

# Konfiguriere Logging
def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """
    Konfiguriere das Logging für das Skript.
    
    Args:
        level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Pfad zur Log-Datei (optional)
        log_format: Format der Log-Nachrichten
        
    Returns:
        Logger-Instanz
    """
    # Konvertiere String-Level in Logging-Level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Ungültiges Log-Level: {level}")
    
    # Konfiguriere Root-Logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Erstelle Logger für das Skript
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
    
    # Füge Datei-Handler hinzu, falls angegeben
    if log_file:
        # Erstelle Verzeichnis, falls es nicht existiert
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    return logger

# Standard-Logger
logger = setup_logging()

# Basisverzeichnisse
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
COMMON_DIR = SCRIPTS_DIR / "common"
SRC_DIR = BASE_DIR / "src"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
DOCKER_DIR = BASE_DIR / "docker-mcp-servers"

# Erstelle Verzeichnisse, falls sie nicht existieren
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class ConfigManager:
    """
    Manager für Konfigurationen aus verschiedenen Quellen.
    
    Diese Klasse bietet Methoden zum Laden, Validieren und Speichern von Konfigurationen
    aus verschiedenen Quellen wie Dateien und Umgebungsvariablen.
    """
    
    def __init__(self, config_dir: Union[str, Path] = CONFIG_DIR):
        """
        Initialisiere den Konfigurationsmanager.
        
        Args:
            config_dir: Verzeichnis für Konfigurationsdateien
        """
        self.config_dir = Path(config_dir)
        self.configs = {}
        
        # Erstelle das Konfigurationsverzeichnis, falls es nicht existiert
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_json_config(self, name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lade eine JSON-Konfigurationsdatei.
        
        Args:
            name: Name der Konfigurationsdatei (ohne .json-Erweiterung)
            default: Standardkonfiguration, falls die Datei nicht existiert
            
        Returns:
            Dict mit der Konfiguration
        """
        config_file = self.config_dir / f"{name}.json"
        
        if name in self.configs:
            return self.configs[name]
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.configs[name] = config
                return config
            except Exception as e:
                logger.error(f"Fehler beim Laden der Konfigurationsdatei {config_file}: {e}")
                if default is not None:
                    logger.info(f"Verwende Standardkonfiguration für {name}")
                    self.configs[name] = default
                    return default
                raise
        else:
            if default is not None:
                logger.info(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standardkonfiguration.")
                self.configs[name] = default
                return default
            else:
                logger.error(f"Konfigurationsdatei {config_file} nicht gefunden und keine Standardkonfiguration angegeben.")
                raise FileNotFoundError(f"Konfigurationsdatei {config_file} nicht gefunden")
    
    def load_yaml_config(self, name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lade eine YAML-Konfigurationsdatei.
        
        Args:
            name: Name der Konfigurationsdatei (ohne .yaml-Erweiterung)
            default: Standardkonfiguration, falls die Datei nicht existiert
            
        Returns:
            Dict mit der Konfiguration
        """
        config_file = self.config_dir / f"{name}.yaml"
        
        if name in self.configs:
            return self.configs[name]
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                self.configs[name] = config
                return config
            except Exception as e:
                logger.error(f"Fehler beim Laden der Konfigurationsdatei {config_file}: {e}")
                if default is not None:
                    logger.info(f"Verwende Standardkonfiguration für {name}")
                    self.configs[name] = default
                    return default
                raise
        else:
            if default is not None:
                logger.info(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standardkonfiguration.")
                self.configs[name] = default
                return default
            else:
                logger.error(f"Konfigurationsdatei {config_file} nicht gefunden und keine Standardkonfiguration angegeben.")
                raise FileNotFoundError(f"Konfigurationsdatei {config_file} nicht gefunden")
    
    def save_json_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Speichere eine Konfiguration als JSON-Datei.
        
        Args:
            name: Name der Konfigurationsdatei (ohne .json-Erweiterung)
            config: Konfiguration, die gespeichert werden soll
        """
        config_file = self.config_dir / f"{name}.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.configs[name] = config
            logger.info(f"Konfiguration {name} erfolgreich gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfigurationsdatei {config_file}: {e}")
            raise
    
    def save_yaml_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Speichere eine Konfiguration als YAML-Datei.
        
        Args:
            name: Name der Konfigurationsdatei (ohne .yaml-Erweiterung)
            config: Konfiguration, die gespeichert werden soll
        """
        config_file = self.config_dir / f"{name}.yaml"
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            self.configs[name] = config
            logger.info(f"Konfiguration {name} erfolgreich gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfigurationsdatei {config_file}: {e}")
            raise
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """
        Hole eine bereits geladene Konfiguration.
        
        Args:
            name: Name der Konfiguration
            
        Returns:
            Dict mit der Konfiguration
            
        Raises:
            KeyError: Wenn die Konfiguration nicht geladen wurde
        """
        if name not in self.configs:
            raise KeyError(f"Konfiguration {name} wurde nicht geladen")
        
        return self.configs[name]
    
    def update_config(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiere eine Konfiguration.
        
        Args:
            name: Name der Konfiguration
            updates: Aktualisierungen für die Konfiguration
            
        Returns:
            Dict mit der aktualisierten Konfiguration
            
        Raises:
            KeyError: Wenn die Konfiguration nicht geladen wurde
        """
        if name not in self.configs:
            raise KeyError(f"Konfiguration {name} wurde nicht geladen")
        
        config = self.configs[name]
        self._deep_update(config, updates)
        self.configs[name] = config
        
        return config
    
    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> None:
        """
        Aktualisiere ein Dictionary rekursiv.
        
        Args:
            d: Dictionary, das aktualisiert werden soll
            u: Dictionary mit Aktualisierungen
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
    
    def load_env_config(self, prefix: str = "", env_vars: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Lade Konfiguration aus Umgebungsvariablen.
        
        Args:
            prefix: Präfix für Umgebungsvariablen
            env_vars: Liste von Umgebungsvariablen, die geladen werden sollen
            
        Returns:
            Dict mit der Konfiguration
        """
        config = {}
        
        # Wenn keine spezifischen Umgebungsvariablen angegeben wurden, lade alle
        if env_vars is None:
            # Lade alle Umgebungsvariablen mit dem angegebenen Präfix
            for key, value in os.environ.items():
                if prefix and not key.startswith(prefix):
                    continue
                
                # Entferne das Präfix
                if prefix:
                    config_key = key[len(prefix):].lower()
                else:
                    config_key = key.lower()
                
                # Konvertiere den Wert
                config[config_key] = self._convert_env_value(value)
        else:
            # Lade nur die angegebenen Umgebungsvariablen
            for key in env_vars:
                env_key = f"{prefix}{key}" if prefix else key
                value = os.environ.get(env_key)
                
                if value is not None:
                    config[key.lower()] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Konvertiere einen Umgebungsvariablenwert in den entsprechenden Python-Typ.
        
        Args:
            value: Wert der Umgebungsvariable
            
        Returns:
            Konvertierter Wert
        """
        # Versuche, den Wert als JSON zu parsen
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Versuche, den Wert als Zahl zu parsen
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Versuche, den Wert als Boolean zu parsen
        if value.lower() in ('true', 'yes', '1', 'y'):
            return True
        elif value.lower() in ('false', 'no', '0', 'n'):
            return False
        
        # Ansonsten gib den Wert als String zurück
        return value
    
    def load_env_file(self, env_file: Union[str, Path] = ".env") -> Dict[str, Any]:
        """
        Lade Umgebungsvariablen aus einer .env-Datei.
        
        Args:
            env_file: Pfad zur .env-Datei
            
        Returns:
            Dict mit den geladenen Umgebungsvariablen
        """
        env_file = Path(env_file)
        
        if not env_file.exists():
            logger.warning(f".env-Datei nicht gefunden: {env_file}")
            return {}
        
        config = {}
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Überspringe Kommentare und leere Zeilen
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse Key-Value-Paare
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Entferne Anführungszeichen
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Setze Umgebungsvariable
                        os.environ[key] = value
                        
                        # Füge zur Konfiguration hinzu
                        config[key] = self._convert_env_value(value)
            
            logger.info(f"Umgebungsvariablen aus {env_file} geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der .env-Datei {env_file}: {e}")
        
        return config


class DockerUtils:
    """
    Hilfsfunktionen für Docker-Operationen.
    """
    
    @staticmethod
    def check_docker_installed() -> bool:
        """
        Überprüfe, ob Docker installiert ist.
        
        Returns:
            bool: True, wenn Docker installiert ist, sonst False.
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def check_docker_running() -> bool:
        """
        Überprüfe, ob Docker läuft.
        
        Returns:
            bool: True, wenn Docker läuft, sonst False.
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def check_docker_compose_installed() -> bool:
        """
        Überprüfe, ob Docker Compose installiert ist.
        
        Returns:
            bool: True, wenn Docker Compose installiert ist, sonst False.
        """
        try:
            # Versuche zuerst das neue Docker Compose Plugin
            result = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                return True
            
            # Versuche das alte docker-compose Kommando
            result = subprocess.run(
                ["docker-compose", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_docker_compose_command() -> List[str]:
        """
        Ermittle den korrekten Docker Compose Befehl.
        
        Returns:
            List[str]: Liste mit dem Docker Compose Befehl.
        """
        try:
            # Versuche zuerst das neue Docker Compose Plugin
            result = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                return ["docker", "compose"]
            
            # Versuche das alte docker-compose Kommando
            result = subprocess.run(
                ["docker-compose", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                return ["docker-compose"]
            
            # Fallback
            return ["docker-compose"]
        except Exception:
            return ["docker-compose"]
    
    @staticmethod
    def start_docker_compose(compose_file: Union[str, Path], extended: bool = False) -> bool:
        """
        Starte Docker Compose.
        
        Args:
            compose_file: Pfad zur Docker Compose Datei.
            extended: Ob die erweiterte Version gestartet werden soll.
            
        Returns:
            bool: True, wenn erfolgreich, sonst False.
        """
        try:
            compose_file = Path(compose_file)
            
            # Überprüfe, ob Docker läuft
            if not DockerUtils.check_docker_running():
                logger.error("Docker läuft nicht. Bitte starten Sie Docker und versuchen Sie es erneut.")
                return False
            
            # Überprüfe, ob Docker Compose installiert ist
            if not DockerUtils.check_docker_compose_installed():
                logger.error("Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.")
                return False
            
            # Wähle die richtige Compose-Datei
            if extended and compose_file.with_suffix('').with_suffix('.extended.yml').exists():
                compose_file = compose_file.with_suffix('').with_suffix('.extended.yml')
            
            # Starte Docker Compose
            docker_compose = DockerUtils.get_docker_compose_command()
            result = subprocess.run(
                docker_compose + ["-f", str(compose_file), "up", "-d"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Fehler beim Starten von Docker Compose: {result.stderr}")
                return False
            
            logger.info("Docker Compose wurde erfolgreich gestartet.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Starten von Docker Compose: {e}")
            return False
    
    @staticmethod
    def stop_docker_compose(compose_file: Union[str, Path]) -> bool:
        """
        Stoppe Docker Compose.
        
        Args:
            compose_file: Pfad zur Docker Compose Datei.
            
        Returns:
            bool: True, wenn erfolgreich, sonst False.
        """
        try:
            compose_file = Path(compose_file)
            
            # Überprüfe, ob Docker läuft
            if not DockerUtils.check_docker_running():
                logger.error("Docker läuft nicht. Bitte starten Sie Docker und versuchen Sie es erneut.")
                return False
            
            # Stoppe Docker Compose
            docker_compose = DockerUtils.get_docker_compose_command()
            result = subprocess.run(
                docker_compose + ["-f", str(compose_file), "down"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Fehler beim Stoppen von Docker Compose: {result.stderr}")
                return False
            
            logger.info("Docker Compose wurde erfolgreich gestoppt.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Stoppen von Docker Compose: {e}")
            return False
    
    @staticmethod
    def get_docker_container_id(container_name: str) -> Optional[str]:
        """
        Hole die ID eines Docker-Containers.
        
        Args:
            container_name: Name des Containers.
            
        Returns:
            Optional[str]: Container-ID oder None, wenn der Container nicht gefunden wurde.
        """
        try:
            # Suche nach dem Container
            result = subprocess.run(
                ["docker", "ps", "-aqf", f"name={container_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Container-ID für {container_name}: {e}")
            return None
    
    @staticmethod
    def is_docker_container_running(container_name: str) -> bool:
        """
        Überprüfe, ob ein Docker-Container läuft.
        
        Args:
            container_name: Name des Containers.
            
        Returns:
            bool: True, wenn der Container läuft, sonst False.
        """
        try:
            # Hole die Container-ID
            container_id = DockerUtils.get_docker_container_id(container_name)
            if not container_id:
                return False
            
            # Überprüfe den Status
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Status}}", container_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                capture_output=True
            )
            
            return result.stdout.strip() == "running"
        except Exception as e:
            logger.error(f"Fehler beim Überprüfen des Docker-Status für {container_name}: {e}")
            return False
    
    @staticmethod
    def get_docker_container_logs(container_name: str, lines: int = 100) -> str:
        """
        Rufe die Logs eines Docker-Containers ab.
        
        Args:
            container_name: Name des Containers.
            lines: Anzahl der Zeilen, die abgerufen werden sollen.
            
        Returns:
            str: Logs des Containers.
        """
        try:
            # Hole die Container-ID
            container_id = DockerUtils.get_docker_container_id(container_name)
            if not container_id:
                return "Container not found"
            
            # Rufe die Logs ab
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                capture_output=True
            )
            
            return result.stdout
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Logs für Container {container_name}: {e}")
            return f"Error retrieving logs: {str(e)}"


class ProcessManager:
    """
    Manager für Prozesse.
    """
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """
        Überprüfe, ob ein Prozess läuft.
        
        Args:
            pid: Prozess-ID
            
        Returns:
            bool: True, wenn der Prozess läuft, sonst False
        """
        try:
            # Überprüfe, ob der Prozess existiert
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    @staticmethod
    def is_process_running_by_name(process_name: str) -> bool:
        """
        Überprüfe, ob ein Prozess mit dem angegebenen Namen läuft.
        
        Args:
            process_name: Name des Prozesses
            
        Returns:
            bool: True, wenn der Prozess läuft, sonst False
        """
        try:
            # Verwende pgrep, um nach dem Prozess zu suchen
            result = subprocess.run(
                ["pgrep", "-f", process_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def kill_process(pid: int, force: bool = False) -> bool:
        """
        Beende einen Prozess.
        
        Args:
            pid: Prozess-ID
            force: Ob der Prozess mit SIGKILL beendet werden soll
            
        Returns:
            bool: True, wenn der Prozess beendet wurde, sonst False
        """
        try:
            # Sende SIGTERM oder SIGKILL
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
            
            # Warte kurz und überprüfe, ob der Prozess beendet wurde
            time.sleep(0.5)
            if ProcessManager.is_process_running(pid):
                if not force:
                    # Versuche es mit SIGKILL
                    return ProcessManager.kill_process(pid, True)
                return False
            
            return True
        except OSError:
            # Prozess existiert nicht
            return True
        except Exception as e:
            logger.error(f"Fehler beim Beenden des Prozesses {pid}: {e}")
            return False
    
    @staticmethod
    def kill_process_by_name(process_name: str, force: bool = False) -> bool:
        """
        Beende alle Prozesse mit dem angegebenen Namen.
        
        Args:
            process_name: Name des Prozesses
            force: Ob die Prozesse mit SIGKILL beendet werden sollen
            
        Returns:
            bool: True, wenn alle Prozesse beendet wurden, sonst False
        """
        try:
            # Verwende pkill, um die Prozesse zu beenden
            signal_option = "-9" if force else ""
            result = subprocess.run(
                ["pkill", signal_option, "-f", process_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            # Überprüfe, ob die Prozesse beendet wurden
            if result.returncode != 0:
                # Keine Prozesse gefunden oder Fehler
                return True
            
            # Warte kurz und überprüfe, ob die Prozesse beendet wurden
            time.sleep(0.5)
            if ProcessManager.is_process_running_by_name(process_name):
                if not force:
                    # Versuche es mit SIGKILL
                    return ProcessManager.kill_process_by_name(process_name, True)
                return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Beenden der Prozesse mit Namen {process_name}: {e}")
            return False
    
    @staticmethod
    def start_process(command: List[str], log_file: Optional[Union[str, Path]] = None, pid_file: Optional[Union[str, Path]] = None) -> Tuple[bool, Optional[int]]:
        """
        Starte einen Prozess.
        
        Args:
            command: Befehl zum Starten des Prozesses
            log_file: Pfad zur Log-Datei
            pid_file: Pfad zur PID-Datei
            
        Returns:
            Tuple[bool, Optional[int]]: (Erfolg, Prozess-ID)
        """
        try:
            # Öffne Log-Datei, falls angegeben
            if log_file:
                log_file = Path(log_file)
                os.makedirs(log_file.parent, exist_ok=True)
                log_fd = open(log_file, 'w')
            else:
                log_fd = subprocess.DEVNULL
            
            # Starte den Prozess
            process = subprocess.Popen(
                command,
                stdout=log_fd,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            
            # Speichere die PID, falls angegeben
            if pid_file:
                pid_file = Path(pid_file)
                os.makedirs(pid_file.parent, exist_ok=True)
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
            
            # Warte kurz und überprüfe, ob der Prozess läuft
            time.sleep(0.5)
            if ProcessManager.is_process_running(process.pid):
                return True, process.pid
            
            return False, None
        except Exception as e:
            logger.error(f"Fehler beim Starten des Prozesses: {e}")
            return False, None


class NetworkUtils:
    """
    Hilfsfunktionen für Netzwerkoperationen.
    """
    
    @staticmethod
    def is_port_in_use(port: int, host: str = "localhost") -> bool:
        """
        Überprüfe, ob ein Port bereits verwendet wird.
        
        Args:
            port: Port-Nummer
            host: Host-Name oder IP-Adresse
            
        Returns:
            bool: True, wenn der Port verwendet wird, sonst False
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    @staticmethod
    def find_free_port(start_port: int = 8000, end_port: int = 9000, host: str = "localhost") -> Optional[int]:
        """
        Finde einen freien Port.
        
        Args:
            start_port: Startport
            end_port: Endport
            host: Host-Name oder IP-Adresse
            
        Returns:
            Optional[int]: Freier Port oder None, wenn kein freier Port gefunden wurde
        """
        for port in range(start_port, end_port + 1):
            if not NetworkUtils.is_port_in_use(port, host):
                return port
        
        return None
    
    @staticmethod
    def wait_for_port(port: int, host: str = "localhost", timeout: int = 30) -> bool:
        """
        Warte, bis ein Port verfügbar ist.
        
        Args:
            port: Port-Nummer
            host: Host-Name oder IP-Adresse
            timeout: Timeout in Sekunden
            
        Returns:
            bool: True, wenn der Port verfügbar ist, sonst False
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if NetworkUtils.is_port_in_use(port, host):
                return True
            
            time.sleep(0.5)
        
        return False


class SystemUtils:
    """
    Hilfsfunktionen für Systemoperationen.
    """
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Hole Systeminformationen.
        
        Returns:
            Dict[str, Any]: Systeminformationen
        """
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "hostname": platform.node(),
            "username": os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown'),
            "home_directory": os.path.expanduser("~"),
            "current_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Füge CPU-Informationen hinzu, falls verfügbar
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count()
            info["cpu_percent"] = psutil.cpu_percent(interval=1)
            info["memory_total"] = psutil.virtual_memory().total
            info["memory_available"] = psutil.virtual_memory().available
            info["memory_percent"] = psutil.virtual_memory().percent
            info["disk_total"] = psutil.disk_usage('/').total
            info["disk_free"] = psutil.disk_usage('/').free
            info["disk_percent"] = psutil.disk_usage('/').percent
        except ImportError:
            pass
        
        return info
    
    @staticmethod
    def check_command(command: str) -> bool:
        """
        Überprüfe, ob ein Befehl verfügbar ist.
        
        Args:
            command: Befehl
            
        Returns:
            bool: True, wenn der Befehl verfügbar ist, sonst False
        """
        try:
            subprocess.run(
                ["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_python_package(package: str) -> bool:
        """
        Überprüfe, ob ein Python-Paket installiert ist.
        
        Args:
            package: Paketname
            
        Returns:
            bool: True, wenn das Paket installiert ist, sonst False
        """
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_python_package(package: str) -> bool:
        """
        Installiere ein Python-Paket.
        
        Args:
            package: Paketname
            
        Returns:
            bool: True, wenn das Paket erfolgreich installiert wurde, sonst False
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False


def parse_arguments(description: str, epilog: str = "") -> argparse.Namespace:
    """
    Parse Kommandozeilenargumente.
    
    Args:
        description: Beschreibung des Skripts
        epilog: Epilog für die Hilfe
        
    Returns:
        argparse.Namespace: Geparste Argumente
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    
    # Allgemeine Argumente
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    parser.add_argument("--quiet", "-q", action="store_true", help="Keine Ausgabe")
    parser.add_argument("--log-file", "-l", help="Pfad zur Log-Datei")
    parser.add_argument("--log-level", choices=["debug", "info", "warning", "error", "critical"], default="info", help="Log-Level")
    parser.add_argument("--config", "-c", help="Pfad zur Konfigurationsdatei")
    parser.add_argument("--env-file", "-e", help="Pfad zur .env-Datei")
    
    return parser.parse_args()


def main():
    """
    Hauptfunktion für Skripte.
    """
    # Parse Argumente
    args = parse_arguments("Gemeinsame Python-Bibliothek für das Dev-Server-Workflow-Projekt")
    
    # Konfiguriere Logging
    log_level = "DEBUG" if args.verbose else "ERROR" if args.quiet else args.log_level.upper()
    setup_logging(log_level, args.log_file)
    
    # Lade Konfiguration
    config_manager = ConfigManager()
    
    if args.env_file:
        config_manager.load_env_file(args.env_file)
    
    if args.config:
        if args.config.endswith(".json"):
            config = config_manager.load_json_config("custom", {})
        elif args.config.endswith(".yaml") or args.config.endswith(".yml"):
            config = config_manager.load_yaml_config("custom", {})
        else:
            logger.error(f"Unbekanntes Konfigurationsformat: {args.config}")
            sys.exit(1)
    
    # Zeige Systeminformationen
    logger.info("Systeminformationen:")
    for key, value in SystemUtils.get_system_info().items():
        logger.info(f"  {key}: {value}")
    
    # Überprüfe Docker
    if DockerUtils.check_docker_installed():
        logger.info("Docker ist installiert.")
        if DockerUtils.check_docker_running():
            logger.info("Docker läuft.")
        else:
            logger.warning("Docker ist installiert, läuft aber nicht.")
    else:
        logger.warning("Docker ist nicht installiert.")
    
    # Überprüfe Docker Compose
    if DockerUtils.check_docker_compose_installed():
        logger.info("Docker Compose ist installiert.")
    else:
        logger.warning("Docker Compose ist nicht installiert.")
    
    logger.info("Gemeinsame Python-Bibliothek erfolgreich geladen.")


if __name__ == "__main__":
    main()