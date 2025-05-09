#!/usr/bin/env python3
"""
Dev-Server Web UI

Implementiert eine Web-UI für den Dev-Server, die Zugriff auf verschiedene Dienste ermöglicht.
"""

import os
import logging
import argparse
import asyncio
from aiohttp import web
import aiohttp_cors
import json
from pathlib import Path

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("dev-server-web-ui.log")
    ]
)
logger = logging.getLogger("dev-server-web-ui")

class DevServerWebUI:
    """Web-UI für den Dev-Server."""

    def __init__(self, config_path=None):
        """Initialisiert die Web-UI mit Konfiguration.

        Args:
            config_path: Pfad zur Konfigurationsdatei
        """
        self.config_path = config_path or Path.home() / ".dev-server-web-ui.json"
        self.services = {
            "n8n": {
                "name": "n8n",
                "url": "https://n8n.ecospherenet.work",
                "description": "Workflow-Automatisierung",
                "icon": "mdi-sitemap"
            },
            "appflowy": {
                "name": "AppFlowy",
                "url": "https://appflowy.ecospherenet.work",
                "description": "Notizen und Dokumentation",
                "icon": "mdi-note-text"
            },
            "openproject": {
                "name": "OpenProject",
                "url": "https://openproject.ecospherenet.work",
                "description": "Projektmanagement",
                "icon": "mdi-calendar-check"
            },
            "gitlab": {
                "name": "GitLab",
                "url": "https://gitlab.ecospherenet.work",
                "description": "Code-Repository",
                "icon": "mdi-git"
            },
            "affine": {
                "name": "Affine",
                "url": "https://affine.ecospherenet.work",
                "description": "Kollaborative Dokumente",
                "icon": "mdi-file-document-edit"
            },
            "dev-server": {
                "name": "Dev-Server",
                "url": "https://dev-server.ecospherenet.work",
                "description": "Entwicklungsserver",
                "icon": "mdi-server"
            }
        }
        self.load_config()

    def load_config(self):
        """Lädt die Konfiguration aus der Datei."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    if 'services' in config:
                        # Aktualisiere die Services mit den Werten aus der Konfiguration
                        for service_id, service_config in config['services'].items():
                            if service_id in self.services:
                                self.services[service_id].update(service_config)
                            else:
                                self.services[service_id] = service_config
                logger.info(f"Konfiguration geladen: {len(self.services)} Dienste gefunden")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Konfiguration: {e}")

    def save_config(self):
        """Speichert die Konfiguration in der Datei."""
        try:
            config = {
                'services': self.services
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Konfiguration gespeichert: {len(self.services)} Dienste")
        except Exception as e:
            logger.warning(f"Fehler beim Speichern der Konfiguration: {e}")

    async def start_server(self, host='0.0.0.0', port=8080):
        """Startet den Web-Server.

        Args:
            host: Host-Adresse für den Server
            port: Port für den Server
        """
        app = web.Application()
        
        # Konfiguriere CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            )
        })
        
        # Statische Dateien
        app.router.add_static('/static', Path(__file__).parent / 'static')
        
        # API-Routen
        async def handle_get_services(request):
            return web.json_response(self.services)
        
        async def handle_add_service(request):
            try:
                data = await request.json()
                service_id = data.get('id')
                if not service_id:
                    return web.json_response({"error": "Service-ID ist erforderlich"}, status=400)
                
                self.services[service_id] = {
                    "name": data.get('name', service_id),
                    "url": data.get('url', ''),
                    "description": data.get('description', ''),
                    "icon": data.get('icon', 'mdi-web')
                }
                self.save_config()
                return web.json_response({"success": True, "service": self.services[service_id]})
            except Exception as e:
                logger.error(f"Fehler beim Hinzufügen des Dienstes: {e}")
                return web.json_response({"error": str(e)}, status=500)
        
        async def handle_update_service(request):
            try:
                service_id = request.match_info['id']
                if service_id not in self.services:
                    return web.json_response({"error": f"Dienst {service_id} nicht gefunden"}, status=404)
                
                data = await request.json()
                self.services[service_id].update({
                    "name": data.get('name', self.services[service_id]['name']),
                    "url": data.get('url', self.services[service_id]['url']),
                    "description": data.get('description', self.services[service_id]['description']),
                    "icon": data.get('icon', self.services[service_id]['icon'])
                })
                self.save_config()
                return web.json_response({"success": True, "service": self.services[service_id]})
            except Exception as e:
                logger.error(f"Fehler beim Aktualisieren des Dienstes: {e}")
                return web.json_response({"error": str(e)}, status=500)
        
        async def handle_delete_service(request):
            try:
                service_id = request.match_info['id']
                if service_id not in self.services:
                    return web.json_response({"error": f"Dienst {service_id} nicht gefunden"}, status=404)
                
                del self.services[service_id]
                self.save_config()
                return web.json_response({"success": True})
            except Exception as e:
                logger.error(f"Fehler beim Löschen des Dienstes: {e}")
                return web.json_response({"error": str(e)}, status=500)
        
        # Hauptseite
        async def handle_index(request):
            with open(Path(__file__).parent / 'static' / 'index.html', 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        
        # Registriere Routen
        api_routes = [
            web.get('/api/services', handle_get_services),
            web.post('/api/services', handle_add_service),
            web.put('/api/services/{id}', handle_update_service),
            web.delete('/api/services/{id}', handle_delete_service),
            web.get('/', handle_index),
            web.get('/{path:.*}', handle_index)  # Alle anderen Pfade zur Index-Seite umleiten
        ]
        
        for route in api_routes:
            cors.add(route)
            app.router.add_route(route.method, route.path, route.handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Web-UI-Server gestartet auf http://{host}:{port}")
        
        return runner

async def main():
    """Hauptfunktion zum Starten des Web-UI-Servers."""
    parser = argparse.ArgumentParser(description='Dev-Server Web UI')
    parser.add_argument('--config', default=os.environ.get('DEV_SERVER_WEB_UI_CONFIG', ''),
                        help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host für den Web-Server')
    parser.add_argument('--port', type=int, default=int(os.environ.get('DEV_SERVER_WEB_UI_PORT', '8080')),
                        help='Port für den Web-Server')
    
    args = parser.parse_args()
    
    # Erstelle und initialisiere den Server
    server = DevServerWebUI(args.config)
    runner = await server.start_server(args.host, args.port)
    
    # Halte den Server am Laufen
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())