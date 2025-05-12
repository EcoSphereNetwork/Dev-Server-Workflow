"""
Erweiterungen für den Authentifizierungsmanager.

Diese Funktionen erweitern den bestehenden AuthManager um API-spezifische Berechtigungen.
"""

def authorize_api_access(self, token: str, resource: str, action: str) -> bool:
    """
    Prüfe, ob ein Token Zugriff auf eine bestimmte API-Ressource und -Aktion hat.
    
    Args:
        token: Der zu autorisierende Token
        resource: Die zu überprüfende Ressource
        action: Die zu überprüfende Aktion
        
    Returns:
        True, wenn der Token die Berechtigung hat, sonst False
    """
    if not self.authenticate(token):
        return False
        
    # Wenn die Authentifizierung deaktiviert ist, immer True zurückgeben
    if not self._settings.AUTH_ENABLED:
        return True
        
    permissions = self.tokens[token].get("permissions", [])
    
    # Wildcard-Berechtigung (alle Ressourcen/Aktionen)
    if "*" in permissions:
        return True
        
    # Ressourcen-Wildcard (alle Aktionen für diese Ressource)
    if f"{resource}:*" in permissions:
        return True
        
    # Spezifische Berechtigung
    if f"{resource}:{action}" in permissions:
        return True
        
    # Generelle API-Berechtigung
    if "api:*" in permissions:
        return True
        
    return False
