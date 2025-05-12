"""
Fehlerbehandlung für MCP-Client und -Server.

Dieses Modul definiert Ausnahmen für die MCP-Kommunikation.
"""

class MCPError(Exception):
    """Basisklasse für MCP-Fehler."""
    pass

class MCPConnectionError(MCPError):
    """Fehler bei der Verbindung zu einem MCP-Server."""
    pass

class MCPServerError(MCPError):
    """Fehler vom MCP-Server."""
    pass

class MCPToolError(MCPError):
    """Fehler bei der Ausführung eines MCP-Tools."""
    pass

class MCPAuthenticationError(MCPError):
    """Fehler bei der Authentifizierung am MCP-Server."""
    pass

class MCPAuthorizationError(MCPError):
    """Fehler bei der Autorisierung am MCP-Server."""
    pass

class MCPRateLimitError(MCPError):
    """Fehler bei Überschreitung des Rate-Limits."""
    pass

def handle_mcp_error(error: Exception) -> str:
    """
    Behandle MCP-Fehler und gib eine benutzerfreundliche Nachricht zurück.
    
    Args:
        error: Die aufgetretene Ausnahme
    
    Returns:
        Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(error, MCPConnectionError):
        return f"Verbindungsfehler: Es konnte keine Verbindung zum MCP-Server hergestellt werden. Details: {str(error)}"
    elif isinstance(error, MCPServerError):
        return f"Server-Fehler: Der MCP-Server hat einen Fehler zurückgegeben. Details: {str(error)}"
    elif isinstance(error, MCPToolError):
        return f"Tool-Fehler: Bei der Ausführung des Tools ist ein Fehler aufgetreten. Details: {str(error)}"
    elif isinstance(error, MCPAuthenticationError):
        return f"Authentifizierungsfehler: Die Authentifizierung am MCP-Server ist fehlgeschlagen. Details: {str(error)}"
    elif isinstance(error, MCPAuthorizationError):
        return f"Autorisierungsfehler: Sie haben keine Berechtigung für diese Aktion. Details: {str(error)}"
    elif isinstance(error, MCPRateLimitError):
        return f"Rate-Limit-Fehler: Sie haben das Rate-Limit überschritten. Details: {str(error)}"
    else:
        return f"Unbekannter Fehler: {str(error)}"
