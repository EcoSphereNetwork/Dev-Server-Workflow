"""
Audit-Modul für den Docker MCP Server.

Dieses Modul bietet Funktionen zur Protokollierung von Audit-Ereignissen.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.logger import logger
from ..core.config import settings


class AuditLogger:
    """Audit-Logger-Klasse."""
    
    def __init__(self, audit_file: Optional[Path] = None):
        """
        Initialisiere den Audit-Logger.
        
        Args:
            audit_file: Pfad zur Audit-Datei
        """
        self.audit_file = audit_file or settings.AUDIT_LOG_FILE
        self.enabled = settings.AUDIT_ENABLED
        
        # Stelle sicher, dass das Verzeichnis existiert
        if self.enabled:
            self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, event: str, user: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Protokolliere ein Audit-Ereignis.
        
        Args:
            event: Das zu protokollierende Ereignis
            user: Der Benutzer, der das Ereignis ausgelöst hat
            details: Details zum Ereignis
        """
        if not self.enabled:
            return
        
        try:
            # Erstelle den Audit-Eintrag
            audit_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "event": event,
                "user": user or "anonymous",
                "details": details or {},
            }
            
            # Schreibe den Audit-Eintrag in die Datei
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            logger.error(f"Fehler beim Protokollieren des Audit-Ereignisses: {e}")
    
    def get_logs(self, limit: int = 100, offset: int = 0, filter_event: Optional[str] = None, filter_user: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Erhalte die Audit-Logs.
        
        Args:
            limit: Maximale Anzahl der zurückzugebenden Logs
            offset: Offset für die Logs
            filter_event: Filter für Ereignisse
            filter_user: Filter für Benutzer
            
        Returns:
            Die Audit-Logs
        """
        if not self.enabled:
            return []
        
        try:
            # Überprüfe, ob die Audit-Datei existiert
            if not self.audit_file.exists():
                return []
            
            # Lese die Audit-Datei
            with open(self.audit_file, "r") as f:
                lines = f.readlines()
            
            # Parse die Audit-Einträge
            audit_entries = []
            for line in lines:
                try:
                    entry = json.loads(line)
                    
                    # Filtere nach Ereignis
                    if filter_event and entry.get("event") != filter_event:
                        continue
                    
                    # Filtere nach Benutzer
                    if filter_user and entry.get("user") != filter_user:
                        continue
                    
                    audit_entries.append(entry)
                except Exception as e:
                    logger.error(f"Fehler beim Parsen des Audit-Eintrags: {e}")
            
            # Sortiere die Audit-Einträge nach Zeitstempel (neueste zuerst)
            audit_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Wende Limit und Offset an
            return audit_entries[offset:offset + limit]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Audit-Logs: {e}")
            return []