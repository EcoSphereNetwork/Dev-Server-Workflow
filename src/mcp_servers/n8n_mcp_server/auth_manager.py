"""
Erweiterter Authentifizierungsmanager für die n8n-API.

Dieses Modul bietet erweiterte Funktionen zur Authentifizierung von n8n-API-Anfragen.
"""

import time
from typing import Dict, List, Any, Optional

class RateLimiter:
    """Rate-Limiter für API-Zugriffe."""
    
    def __init__(self):
        self.limits = {}  # Token -> {count, last_reset}
        
    async def check_limit(self, token: str, limit: int, window: int) -> bool:
        """
        Prüfe, ob ein Token sein Limit überschritten hat.
        
        Args:
            token: Der zu prüfende Token
            limit: Das maximale Limit pro Fenster
            window: Das Zeitfenster in Sekunden
            
        Returns:
            True, wenn das Limit nicht überschritten wurde, sonst False
        """
        now = time.time()
        
        if token not in self.limits:
            self.limits[token] = {"count": 1, "last_reset": now}
            return True
            
        # Reset, wenn Zeitfenster abgelaufen
        if now - self.limits[token]["last_reset"] > window:
            self.limits[token] = {"count": 1, "last_reset": now}
            return True
            
        # Prüfe Limit
        if self.limits[token]["count"] >= limit:
            return False
            
        # Inkrementiere Zähler
        self.limits[token]["count"] += 1
        return True
