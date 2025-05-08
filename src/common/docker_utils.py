"""
Gemeinsame Docker-Hilfsfunktionen für das Dev-Server-Workflow-Projekt.
"""

import os
import subprocess
import logging
from typing import List, Optional, Tuple, Dict, Any, Union

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docker-utils')


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


def start_docker_compose(compose_file: str, extended: bool = False) -> bool:
    """
    Starte Docker Compose.
    
    Args:
        compose_file: Pfad zur Docker Compose Datei.
        extended: Ob die erweiterte Version gestartet werden soll.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob Docker läuft
        if not check_docker_running():
            logger.error("Docker läuft nicht. Bitte starten Sie Docker und versuchen Sie es erneut.")
            return False
        
        # Überprüfe, ob Docker Compose installiert ist
        if not check_docker_compose_installed():
            logger.error("Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.")
            return False
        
        # Wähle die richtige Compose-Datei
        if extended and os.path.exists(compose_file.replace('.yml', '-extended.yml')):
            compose_file = compose_file.replace('.yml', '-extended.yml')
        
        # Starte Docker Compose
        docker_compose = get_docker_compose_command()
        result = subprocess.run(
            docker_compose + ["-f", compose_file, "up", "-d"],
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


def stop_docker_compose(compose_file: str) -> bool:
    """
    Stoppe Docker Compose.
    
    Args:
        compose_file: Pfad zur Docker Compose Datei.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob Docker läuft
        if not check_docker_running():
            logger.error("Docker läuft nicht. Bitte starten Sie Docker und versuchen Sie es erneut.")
            return False
        
        # Stoppe Docker Compose
        docker_compose = get_docker_compose_command()
        result = subprocess.run(
            docker_compose + ["-f", compose_file, "down"],
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


def restart_docker_compose(compose_file: str) -> bool:
    """
    Starte Docker Compose neu.
    
    Args:
        compose_file: Pfad zur Docker Compose Datei.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob Docker läuft
        if not check_docker_running():
            logger.error("Docker läuft nicht. Bitte starten Sie Docker und versuchen Sie es erneut.")
            return False
        
        # Starte Docker Compose neu
        docker_compose = get_docker_compose_command()
        result = subprocess.run(
            docker_compose + ["-f", compose_file, "restart"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Fehler beim Neustarten von Docker Compose: {result.stderr}")
            return False
        
        logger.info("Docker Compose wurde erfolgreich neu gestartet.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Neustarten von Docker Compose: {e}")
        return False


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
        container_id = get_docker_container_id(container_name)
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


def start_docker_container(container_name: str) -> bool:
    """
    Starte einen Docker-Container.
    
    Args:
        container_name: Name des Containers.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob der Container bereits läuft
        if is_docker_container_running(container_name):
            logger.info(f"Container {container_name} läuft bereits.")
            return True
        
        # Hole die Container-ID
        container_id = get_docker_container_id(container_name)
        if not container_id:
            logger.error(f"Container {container_name} nicht gefunden.")
            return False
        
        # Starte den Container
        result = subprocess.run(
            ["docker", "start", container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Fehler beim Starten des Containers {container_name}: {result.stderr}")
            return False
        
        logger.info(f"Container {container_name} wurde erfolgreich gestartet.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Starten des Containers {container_name}: {e}")
        return False


def stop_docker_container(container_name: str) -> bool:
    """
    Stoppe einen Docker-Container.
    
    Args:
        container_name: Name des Containers.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob der Container läuft
        if not is_docker_container_running(container_name):
            logger.info(f"Container {container_name} läuft nicht.")
            return True
        
        # Hole die Container-ID
        container_id = get_docker_container_id(container_name)
        if not container_id:
            logger.error(f"Container {container_name} nicht gefunden.")
            return False
        
        # Stoppe den Container
        result = subprocess.run(
            ["docker", "stop", container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Fehler beim Stoppen des Containers {container_name}: {result.stderr}")
            return False
        
        logger.info(f"Container {container_name} wurde erfolgreich gestoppt.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Stoppen des Containers {container_name}: {e}")
        return False


def restart_docker_container(container_name: str) -> bool:
    """
    Starte einen Docker-Container neu.
    
    Args:
        container_name: Name des Containers.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Hole die Container-ID
        container_id = get_docker_container_id(container_name)
        if not container_id:
            logger.error(f"Container {container_name} nicht gefunden.")
            return False
        
        # Starte den Container neu
        result = subprocess.run(
            ["docker", "restart", container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Fehler beim Neustarten des Containers {container_name}: {result.stderr}")
            return False
        
        logger.info(f"Container {container_name} wurde erfolgreich neu gestartet.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Neustarten des Containers {container_name}: {e}")
        return False


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
        container_id = get_docker_container_id(container_name)
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


def run_docker_command(command: List[str]) -> bool:
    """
    Führe einen Docker-Befehl aus.
    
    Args:
        command: Docker-Befehl als Liste.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        result = subprocess.run(
            ["docker"] + command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Docker-Befehls: {e}")
        return False