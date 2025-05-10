"""
Docker-Executor-Modul für den Docker MCP Server.

Dieses Modul bietet Funktionen zur Interaktion mit Docker.
"""

import os
import json
import logging
import docker
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.logger import logger
from ..core.config import settings


class DockerExecutor:
    """Docker-Executor-Klasse."""
    
    def __init__(self):
        """Initialisiere den Docker-Executor."""
        self.client = self._create_docker_client()
    
    def _create_docker_client(self) -> docker.DockerClient:
        """
        Erstelle einen Docker-Client.
        
        Returns:
            Docker-Client
        """
        try:
            # Erstelle Docker-Client mit den Einstellungen
            client_kwargs = {}
            
            if settings.DOCKER_HOST:
                client_kwargs["base_url"] = settings.DOCKER_HOST
            
            if settings.DOCKER_API_VERSION:
                client_kwargs["version"] = settings.DOCKER_API_VERSION
            
            if settings.DOCKER_TLS_VERIFY:
                client_kwargs["tls"] = True
                
                if settings.DOCKER_CERT_PATH:
                    client_kwargs["cert_path"] = settings.DOCKER_CERT_PATH
            
            return docker.DockerClient(**client_kwargs)
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Docker-Clients: {e}")
            raise
    
    def list_containers(self, all: bool = False) -> List[Dict[str, Any]]:
        """
        Liste alle Container auf.
        
        Args:
            all: Ob alle Container aufgelistet werden sollen
            
        Returns:
            Liste der Container
        """
        try:
            containers = self.client.containers.list(all=all)
            
            # Konvertiere Container in Dictionaries
            container_dicts = []
            for container in containers:
                container_dict = {
                    "id": container.id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.id,
                    "status": container.status,
                    "created": container.attrs["Created"],
                    "ports": container.ports,
                    "labels": container.labels,
                }
                container_dicts.append(container_dict)
            
            return container_dicts
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Container: {e}")
            raise
    
    def get_container(self, container_id: str) -> Dict[str, Any]:
        """
        Erhalte einen Container.
        
        Args:
            container_id: ID oder Name des Containers
            
        Returns:
            Container-Dictionary
        """
        try:
            container = self.client.containers.get(container_id)
            
            # Konvertiere Container in Dictionary
            container_dict = {
                "id": container.id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "status": container.status,
                "created": container.attrs["Created"],
                "ports": container.ports,
                "labels": container.labels,
                "command": container.attrs["Config"]["Cmd"],
                "entrypoint": container.attrs["Config"]["Entrypoint"],
                "env": container.attrs["Config"]["Env"],
                "volumes": container.attrs["Config"]["Volumes"],
                "network_mode": container.attrs["HostConfig"]["NetworkMode"],
                "restart_policy": container.attrs["HostConfig"]["RestartPolicy"],
                "mounts": container.attrs["Mounts"],
            }
            
            return container_dict
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Containers: {e}")
            raise
    
    def start_container(self, container_id: str) -> bool:
        """
        Starte einen Container.
        
        Args:
            container_id: ID oder Name des Containers
            
        Returns:
            True, wenn der Container erfolgreich gestartet wurde, sonst False
        """
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des Containers: {e}")
            return False
    
    def stop_container(self, container_id: str) -> bool:
        """
        Stoppe einen Container.
        
        Args:
            container_id: ID oder Name des Containers
            
        Returns:
            True, wenn der Container erfolgreich gestoppt wurde, sonst False
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Containers: {e}")
            return False
    
    def restart_container(self, container_id: str) -> bool:
        """
        Starte einen Container neu.
        
        Args:
            container_id: ID oder Name des Containers
            
        Returns:
            True, wenn der Container erfolgreich neu gestartet wurde, sonst False
        """
        try:
            container = self.client.containers.get(container_id)
            container.restart()
            return True
        except Exception as e:
            logger.error(f"Fehler beim Neustarten des Containers: {e}")
            return False
    
    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """
        Entferne einen Container.
        
        Args:
            container_id: ID oder Name des Containers
            force: Ob der Container gewaltsam entfernt werden soll
            
        Returns:
            True, wenn der Container erfolgreich entfernt wurde, sonst False
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Entfernen des Containers: {e}")
            return False
    
    def list_images(self) -> List[Dict[str, Any]]:
        """
        Liste alle Images auf.
        
        Returns:
            Liste der Images
        """
        try:
            images = self.client.images.list()
            
            # Konvertiere Images in Dictionaries
            image_dicts = []
            for image in images:
                image_dict = {
                    "id": image.id,
                    "tags": image.tags,
                    "created": image.attrs["Created"],
                    "size": image.attrs["Size"],
                    "labels": image.labels,
                }
                image_dicts.append(image_dict)
            
            return image_dicts
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Images: {e}")
            raise
    
    def get_image(self, image_id: str) -> Dict[str, Any]:
        """
        Erhalte ein Image.
        
        Args:
            image_id: ID oder Name des Images
            
        Returns:
            Image-Dictionary
        """
        try:
            image = self.client.images.get(image_id)
            
            # Konvertiere Image in Dictionary
            image_dict = {
                "id": image.id,
                "tags": image.tags,
                "created": image.attrs["Created"],
                "size": image.attrs["Size"],
                "labels": image.labels,
                "architecture": image.attrs["Architecture"],
                "os": image.attrs["Os"],
                "author": image.attrs.get("Author", ""),
                "comment": image.attrs.get("Comment", ""),
                "config": image.attrs["Config"],
            }
            
            return image_dict
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Images: {e}")
            raise
    
    def pull_image(self, image_name: str) -> bool:
        """
        Ziehe ein Image.
        
        Args:
            image_name: Name des Images
            
        Returns:
            True, wenn das Image erfolgreich gezogen wurde, sonst False
        """
        try:
            self.client.images.pull(image_name)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Ziehen des Images: {e}")
            return False
    
    def remove_image(self, image_id: str, force: bool = False) -> bool:
        """
        Entferne ein Image.
        
        Args:
            image_id: ID oder Name des Images
            force: Ob das Image gewaltsam entfernt werden soll
            
        Returns:
            True, wenn das Image erfolgreich entfernt wurde, sonst False
        """
        try:
            self.client.images.remove(image_id, force=force)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Entfernen des Images: {e}")
            return False
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """
        Liste alle Netzwerke auf.
        
        Returns:
            Liste der Netzwerke
        """
        try:
            networks = self.client.networks.list()
            
            # Konvertiere Netzwerke in Dictionaries
            network_dicts = []
            for network in networks:
                network_dict = {
                    "id": network.id,
                    "name": network.name,
                    "driver": network.attrs["Driver"],
                    "scope": network.attrs["Scope"],
                    "created": network.attrs["Created"],
                    "labels": network.attrs.get("Labels", {}),
                }
                network_dicts.append(network_dict)
            
            return network_dicts
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Netzwerke: {e}")
            raise
    
    def get_network(self, network_id: str) -> Dict[str, Any]:
        """
        Erhalte ein Netzwerk.
        
        Args:
            network_id: ID oder Name des Netzwerks
            
        Returns:
            Netzwerk-Dictionary
        """
        try:
            network = self.client.networks.get(network_id)
            
            # Konvertiere Netzwerk in Dictionary
            network_dict = {
                "id": network.id,
                "name": network.name,
                "driver": network.attrs["Driver"],
                "scope": network.attrs["Scope"],
                "created": network.attrs["Created"],
                "labels": network.attrs.get("Labels", {}),
                "containers": network.attrs["Containers"],
                "options": network.attrs["Options"],
                "ipam": network.attrs["IPAM"],
            }
            
            return network_dict
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Netzwerks: {e}")
            raise
    
    def list_volumes(self) -> List[Dict[str, Any]]:
        """
        Liste alle Volumes auf.
        
        Returns:
            Liste der Volumes
        """
        try:
            volumes = self.client.volumes.list()
            
            # Konvertiere Volumes in Dictionaries
            volume_dicts = []
            for volume in volumes:
                volume_dict = {
                    "id": volume.id,
                    "name": volume.name,
                    "driver": volume.attrs["Driver"],
                    "mountpoint": volume.attrs["Mountpoint"],
                    "created": volume.attrs["CreatedAt"],
                    "labels": volume.attrs.get("Labels", {}),
                }
                volume_dicts.append(volume_dict)
            
            return volume_dicts
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Volumes: {e}")
            raise
    
    def get_volume(self, volume_id: str) -> Dict[str, Any]:
        """
        Erhalte ein Volume.
        
        Args:
            volume_id: ID oder Name des Volumes
            
        Returns:
            Volume-Dictionary
        """
        try:
            volume = self.client.volumes.get(volume_id)
            
            # Konvertiere Volume in Dictionary
            volume_dict = {
                "id": volume.id,
                "name": volume.name,
                "driver": volume.attrs["Driver"],
                "mountpoint": volume.attrs["Mountpoint"],
                "created": volume.attrs["CreatedAt"],
                "labels": volume.attrs.get("Labels", {}),
                "options": volume.attrs["Options"],
                "scope": volume.attrs["Scope"],
            }
            
            return volume_dict
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Volumes: {e}")
            raise