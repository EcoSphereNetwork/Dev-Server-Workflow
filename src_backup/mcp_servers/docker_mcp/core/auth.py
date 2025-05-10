"""
Authentifizierungsmodul für den Docker MCP Server.

Dieses Modul bietet Funktionen zur Authentifizierung von Anfragen.
"""

import os
import json
import logging
import secrets
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.logger import logger
from ..core.config import settings


class AuthManager:
    """Authentifizierungsmanager-Klasse."""
    
    def __init__(self, auth_file: Optional[Path] = None):
        """
        Initialisiere den Authentifizierungsmanager.
        
        Args:
            auth_file: Pfad zur Authentifizierungsdatei
        """
        self.auth_file = auth_file or Path(settings.BASE_DIR) / "config" / "docker_mcp_auth.json"
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, Dict[str, Any]]:
        """
        Lade die Tokens aus der Authentifizierungsdatei.
        
        Returns:
            Die geladenen Tokens
        """
        try:
            if self.auth_file.exists():
                with open(self.auth_file, "r") as f:
                    return json.load(f)
            else:
                # Erstelle Standardtokens
                tokens = {}
                
                # Füge das Token aus den Einstellungen hinzu, wenn vorhanden
                if settings.AUTH_TOKEN:
                    tokens[settings.AUTH_TOKEN] = {
                        "name": "default",
                        "permissions": ["*"],
                    }
                
                # Speichere die Tokens
                self._save_tokens(tokens)
                
                return tokens
        except Exception as e:
            logger.error(f"Fehler beim Laden der Tokens: {e}")
            return {}
    
    def _save_tokens(self, tokens: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """
        Speichere die Tokens in der Authentifizierungsdatei.
        
        Args:
            tokens: Die zu speichernden Tokens
        """
        try:
            tokens = tokens or self.tokens
            
            # Stelle sicher, dass das Verzeichnis existiert
            self.auth_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Speichere die Tokens
            with open(self.auth_file, "w") as f:
                json.dump(tokens, f, indent=2)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Tokens: {e}")
    
    def authenticate(self, token: str) -> bool:
        """
        Authentifiziere einen Token.
        
        Args:
            token: Der zu authentifizierende Token
            
        Returns:
            True, wenn der Token gültig ist, sonst False
        """
        # Wenn die Authentifizierung deaktiviert ist, immer True zurückgeben
        if not settings.AUTH_ENABLED:
            return True
        
        # Überprüfe, ob der Token existiert
        return token in self.tokens
    
    def authorize(self, token: str, permission: str) -> bool:
        """
        Autorisiere einen Token für eine Berechtigung.
        
        Args:
            token: Der zu autorisierende Token
            permission: Die zu überprüfende Berechtigung
            
        Returns:
            True, wenn der Token die Berechtigung hat, sonst False
        """
        # Wenn die Authentifizierung deaktiviert ist, immer True zurückgeben
        if not settings.AUTH_ENABLED:
            return True
        
        # Überprüfe, ob der Token existiert
        if token not in self.tokens:
            return False
        
        # Überprüfe, ob der Token die Berechtigung hat
        permissions = self.tokens[token].get("permissions", [])
        
        # Wenn der Token die Berechtigung "*" hat, hat er alle Berechtigungen
        if "*" in permissions:
            return True
        
        # Überprüfe, ob der Token die Berechtigung hat
        return permission in permissions
    
    def create_token(self, name: str, permissions: List[str]) -> str:
        """
        Erstelle einen neuen Token.
        
        Args:
            name: Name des Tokens
            permissions: Berechtigungen des Tokens
            
        Returns:
            Der erstellte Token
        """
        # Generiere einen zufälligen Token
        token = secrets.token_hex(32)
        
        # Füge den Token hinzu
        self.tokens[token] = {
            "name": name,
            "permissions": permissions,
        }
        
        # Speichere die Tokens
        self._save_tokens()
        
        return token
    
    def revoke_token(self, token: str) -> bool:
        """
        Widerrufe einen Token.
        
        Args:
            token: Der zu widerrufende Token
            
        Returns:
            True, wenn der Token erfolgreich widerrufen wurde, sonst False
        """
        # Überprüfe, ob der Token existiert
        if token not in self.tokens:
            return False
        
        # Entferne den Token
        del self.tokens[token]
        
        # Speichere die Tokens
        self._save_tokens()
        
        return True
    
    def list_tokens(self) -> Dict[str, Dict[str, Any]]:
        """
        Liste alle Tokens auf.
        
        Returns:
            Die Tokens
        """
        return self.tokens