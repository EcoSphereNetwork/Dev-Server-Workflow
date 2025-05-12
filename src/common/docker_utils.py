"""
Docker-Hilfsfunktionen für das Dev-Server-Workflow-Projekt.

Dieses Modul bietet Funktionen zur Interaktion mit Docker-Containern, Docker Compose
und zur Verwaltung von Docker-Ressourcen.
"""

import os
import subprocess
import logging
import time
from pathlib import Path
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
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der Docker-Installation: {e}")
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
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen des Docker-Status: {e}")
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
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der Docker Compose Installation: {e}")
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
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln des Docker Compose Befehls: {e}")
        return ["docker-compose"]


def start_docker_compose(compose_file: Union[str, Path], extended: bool = False, env_file: Optional[Union[str, Path]] = None) -> bool:
    """
    Starte Docker Compose.
    
    Args:
        compose_file: Pfad zur Docker Compose Datei.
        extended: Ob die erweiterte Version gestartet werden soll.
        env_file: Pfad zur Umgebungsvariablen-Datei.
        
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
        
        # Konvertiere Pfade zu Path-Objekten
        compose_file = Path(compose_file)
        if not compose_file.exists():
            logger.error(f"Docker Compose Datei nicht gefunden: {compose_file}")
            return False
        
        # Wähle die richtige Compose-Datei, wenn extended aktiviert ist
        if extended and compose_file.with_suffix('').with_suffix('.extended.yml').exists():
            compose_file = compose_file.with_suffix('').with_suffix('.extended.yml')
        
        # Starte Docker Compose
        docker_compose = get_docker_compose_command()
        cmd = docker_compose + ["-f", str(compose_file), "up", "-d"]
        
        # Füge env-file hinzu, wenn angegeben
        if env_file:
            env_file = Path(env_file)
            if not env_file.exists():
                logger.warning(f"Umgebungsvariablen-Datei nicht gefunden: {env_file}")
            else:
                cmd.extend(["--env-file", str(env_file)])
        
        result = subprocess.run(
            cmd,
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


def stop_docker_compose(compose_file: Union[str, Path]) -> bool:
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
        
        # Konvertiere zu Path-Objekt
        compose_file = Path(compose_file)
        if not compose_file.exists():
            logger.error(f"Docker Compose Datei nicht gefunden: {compose_file}")
            return False
        
        # Stoppe Docker Compose
        docker_compose = get_docker_compose_command()
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


def restart_docker_compose(compose_file: Union[str, Path]) -> bool:
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
        
        # Konvertiere zu Path-Objekt
        compose_file = Path(compose_file)
        if not compose_file.exists():
            logger.error(f"Docker Compose Datei nicht gefunden: {compose_file}")
            return False
        
        # Starte Docker Compose neu
        docker_compose = get_docker_compose_command()
        result = subprocess.run(
            docker_compose + ["-f", str(compose_file), "restart"],
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
        # Überprüfe direkt mit docker ps
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            return bool(container_id)
        
        return False
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen, ob Container {container_name} läuft: {e}")
        return False


def get_docker_container_logs(container_name: str, tail: int = 100) -> Optional[str]:
    """
    Rufe die Logs eines Docker-Containers ab.
    
    Args:
        container_name: Name des Containers.
        tail: Anzahl der Zeilen, die abgerufen werden sollen.
        
    Returns:
        Optional[str]: Container-Logs oder None, wenn ein Fehler aufgetreten ist.
    """
    try:
        result = subprocess.run(
            ["docker", "logs", f"--tail={tail}", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            logger.error(f"Fehler beim Abrufen der Logs für Container {container_name}: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Logs für Container {container_name}: {e}")
        return None


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
        
        # Stoppe den Container
        result = subprocess.run(
            ["docker", "stop", container_name],
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


def remove_docker_container(container_name: str, force: bool = False) -> bool:
    """
    Entferne einen Docker-Container.
    
    Args:
        container_name: Name des Containers.
        force: Erzwinge das Entfernen (auch wenn der Container läuft).
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Bereite das Kommando vor
        cmd = ["docker", "rm"]
        if force:
            cmd.append("-f")
        cmd.append(container_name)
        
        # Führe das Kommando aus
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Fehler beim Entfernen des Containers {container_name}: {result.stderr}")
            return False
        
        logger.info(f"Container {container_name} wurde erfolgreich entfernt.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Entfernen des Containers {container_name}: {e}")
        return False


def create_docker_network(network_name: str) -> bool:
    """
    Erstelle ein Docker-Netzwerk.
    
    Args:
        network_name: Name des Netzwerks.
        
    Returns:
        bool: True, wenn erfolgreich, sonst False.
    """
    try:
        # Überprüfe, ob das Netzwerk bereits existiert
        result = subprocess.run(
            ["docker", "network", "inspect", network_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"Netzwerk {network_name} existiert bereits.")
            return True
        
        # Erstelle das Netzwerk
        result = subprocess.run(
            ["docker", "network", "create", network_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"Netzwerk {network_name} erfolgreich erstellt.")
            return True
        else:
            logger.error(f"Fehler beim Erstellen des Netzwerks {network_name}: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Netzwerks {network_name}: {e}")
        return False


def run_docker_container(
    image: str,
    name: Optional[str] = None,
    ports: Optional[List[str]] = None,
    volumes: Optional[List[str]] = None,
    environment: Optional[Dict[str, str]] = None,
    network: Optional[str] = None,
    command: Optional[List[str]] = None,
    detach: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Starte einen Docker-Container.
    
    Args:
        image: Docker-Image.
        name: Container-Name.
        ports: Port-Mappings ("host:container").
        volumes: Volume-Mappings ("host:container").
        environment: Umgebungsvariablen.
        network: Docker-Netzwerk.
        command: Kommando zum Ausführen.
        detach: Im Hintergrund ausführen.
        
    Returns:
        Tuple[bool, Optional[str]]: (Erfolg, Container-ID oder Output).
    """
    try:
        cmd = ["docker", "run"]
        
        if detach:
            cmd.append("-d")
        
        if name:
            cmd.extend(["--name", name])
        
        if ports:
            for port in ports:
                cmd.extend(["-p", port])
        
        if volumes:
            for volume in volumes:
                cmd.extend(["-v", volume])
        
        if environment:
            for key, value in environment.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        if network:
            cmd.extend(["--network", network])
        
        cmd.append(image)
        
        if command:
            cmd.extend(command)
        
        logger.info(f"Starte Docker-Container: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Container erfolgreich gestartet: {output}")
            return True, output
        else:
            logger.error(f"Fehler beim Starten des Containers: {result.stderr}")
            return False, None
    except Exception as e:
        logger.error(f"Fehler beim Starten des Containers: {e}")
        return False, None


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
        
        if result.returncode == 0:
            logger.info(f"Docker-Befehl erfolgreich ausgeführt: {' '.join(['docker'] + command)}")
            return True
        else:
            logger.error(f"Fehler beim Ausführen des Docker-Befehls: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Docker-Befehls: {e}")
        return False


def inspect_docker_container(container_name: str) -> Optional[Dict[str, Any]]:
    """
    Inspiziere einen Docker-Container.
    
    Args:
        container_name: Name des Containers.
        
    Returns:
        Optional[Dict[str, Any]]: Container-Informationen oder None, wenn ein Fehler aufgetreten ist.
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)[0]
        else:
            logger.error(f"Fehler beim Inspizieren des Containers {container_name}: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Inspizieren des Containers {container_name}: {e}")
        return None


def get_container_ip(container_name: str, network: Optional[str] = None) -> Optional[str]:
    """
    Ermittle die IP-Adresse eines Docker-Containers.
    
    Args:
        container_name: Name des Containers.
        network: Netzwerkname (optional).
        
    Returns:
        Optional[str]: IP-Adresse oder None, wenn ein Fehler aufgetreten ist.
    """
    try:
        inspect_data = inspect_docker_container(container_name)
        if not inspect_data:
            return None
        
        networks = inspect_data.get("NetworkSettings", {}).get("Networks", {})
        
        if network:
            # Wenn ein Netzwerk angegeben wurde, nur dieses Netzwerk prüfen
            if network in networks:
                return networks[network].get("IPAddress")
            else:
                logger.error(f"Container {container_name} ist nicht mit dem Netzwerk {network} verbunden.")
                return None
        else:
            # Ansonsten die erste verfügbare IP-Adresse zurückgeben
            for net_name, net_data in networks.items():
                ip = net_data.get("IPAddress")
                if ip:
                    return ip
            
            # Fallback: Versuche Bridge-Netzwerk
            return networks.get("bridge", {}).get("IPAddress")
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln der IP-Adresse für Container {container_name}: {e}")
        return None
