"""
Zentrales Konfigurationsmanagement für das Dev-Server-Workflow-Projekt.

Dieses Modul bietet eine einheitliche Schnittstelle für den Zugriff auf Konfigurationen
aus verschiedenen Quellen (Dateien, Umgebungsvariablen, etc.) und stellt sicher, dass
die Konfigurationen validiert werden.
"""

import os
import json
import logging
import yaml
from typing import Dict, List, Any, Optional, Union, Callable, Type, TypeVar, Generic

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('config-manager')

# Typ-Variable für generische Typen
T = TypeVar('T')


class ConfigValidationError(Exception):
    """Fehler bei der Validierung einer Konfiguration."""
    
    def __init__(self, message: str, errors: Optional[Dict[str, str]] = None):
        """
        Initialisiere den Validierungsfehler.
        
        Args:
            message: Fehlermeldung
            errors: Detaillierte Fehlerinformationen
        """
        self.errors = errors or {}
        super().__init__(message)


class ConfigManager:
    """
    Manager für Konfigurationen aus verschiedenen Quellen.
    
    Diese Klasse bietet Methoden zum Laden, Validieren und Speichern von Konfigurationen
    aus verschiedenen Quellen wie Dateien und Umgebungsvariablen.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialisiere den Konfigurationsmanager.
        
        Args:
            config_dir: Verzeichnis für Konfigurationsdateien
        """
        self.config_dir = config_dir
        self.configs = {}
        
        # Erstelle das Konfigurationsverzeichnis, falls es nicht existiert
        os.makedirs(config_dir, exist_ok=True)
    
    def load_json_config(self, name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lade eine JSON-Konfigurationsdatei.
        
        Args:
            name: Name der Konfigurationsdatei (ohne .json-Erweiterung)
            default: Standardkonfiguration, falls die Datei nicht existiert
            
        Returns:
            Dict mit der Konfiguration
        """
        config_file = os.path.join(self.config_dir, f"{name}.json")
        
        if name in self.configs:
            return self.configs[name]
        
        if os.path.exists(config_file):
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
        config_file = os.path.join(self.config_dir, f"{name}.yaml")
        
        if name in self.configs:
            return self.configs[name]
        
        if os.path.exists(config_file):
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
        config_file = os.path.join(self.config_dir, f"{name}.json")
        
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
        config_file = os.path.join(self.config_dir, f"{name}.yaml")
        
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
    
    def validate_config(self, name: str, schema: Dict[str, Any]) -> bool:
        """
        Validiere eine Konfiguration gegen ein Schema.
        
        Args:
            name: Name der Konfiguration
            schema: Schema für die Validierung
            
        Returns:
            True, wenn die Konfiguration gültig ist, sonst False
            
        Raises:
            KeyError: Wenn die Konfiguration nicht geladen wurde
            ConfigValidationError: Wenn die Konfiguration ungültig ist
        """
        if name not in self.configs:
            raise KeyError(f"Konfiguration {name} wurde nicht geladen")
        
        config = self.configs[name]
        errors = {}
        
        # Validiere die Konfiguration
        for key, value_schema in schema.items():
            if key not in config:
                if value_schema.get('required', False):
                    errors[key] = f"Pflichtfeld {key} fehlt"
                continue
            
            value = config[key]
            value_type = value_schema.get('type')
            
            if value_type and not self._check_type(value, value_type):
                errors[key] = f"Ungültiger Typ für {key}: {type(value).__name__}, erwartet: {value_type}"
                continue
            
            if 'enum' in value_schema and value not in value_schema['enum']:
                errors[key] = f"Ungültiger Wert für {key}: {value}, erwartet: {value_schema['enum']}"
                continue
            
            if 'min' in value_schema and value < value_schema['min']:
                errors[key] = f"Wert für {key} zu klein: {value}, Minimum: {value_schema['min']}"
                continue
            
            if 'max' in value_schema and value > value_schema['max']:
                errors[key] = f"Wert für {key} zu groß: {value}, Maximum: {value_schema['max']}"
                continue
            
            if 'pattern' in value_schema and not self._check_pattern(value, value_schema['pattern']):
                errors[key] = f"Wert für {key} entspricht nicht dem Muster: {value_schema['pattern']}"
                continue
            
            if 'properties' in value_schema and isinstance(value, dict):
                sub_errors = {}
                for sub_key, sub_schema in value_schema['properties'].items():
                    if sub_key not in value:
                        if sub_schema.get('required', False):
                            sub_errors[sub_key] = f"Pflichtfeld {sub_key} fehlt"
                        continue
                    
                    sub_value = value[sub_key]
                    sub_type = sub_schema.get('type')
                    
                    if sub_type and not self._check_type(sub_value, sub_type):
                        sub_errors[sub_key] = f"Ungültiger Typ für {sub_key}: {type(sub_value).__name__}, erwartet: {sub_type}"
                
                if sub_errors:
                    errors[key] = sub_errors
        
        if errors:
            raise ConfigValidationError(f"Konfiguration {name} ist ungültig", errors)
        
        return True
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Überprüfe, ob ein Wert den erwarteten Typ hat.
        
        Args:
            value: Wert, der überprüft werden soll
            expected_type: Erwarteter Typ
            
        Returns:
            True, wenn der Wert den erwarteten Typ hat, sonst False
        """
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'null':
            return value is None
        else:
            return False
    
    def _check_pattern(self, value: str, pattern: str) -> bool:
        """
        Überprüfe, ob ein Wert einem Muster entspricht.
        
        Args:
            value: Wert, der überprüft werden soll
            pattern: Muster
            
        Returns:
            True, wenn der Wert dem Muster entspricht, sonst False
        """
        import re
        return bool(re.match(pattern, value))
    
    def get_env_config(self, prefix: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hole Konfiguration aus Umgebungsvariablen.
        
        Args:
            prefix: Präfix für Umgebungsvariablen
            schema: Schema für die Validierung
            
        Returns:
            Dict mit der Konfiguration
        """
        config = {}
        
        for key, value_schema in schema.items():
            env_key = f"{prefix}_{key.upper()}"
            env_value = os.environ.get(env_key)
            
            if env_value is None:
                if value_schema.get('required', False):
                    logger.warning(f"Pflichtumgebungsvariable {env_key} nicht gesetzt")
                continue
            
            value_type = value_schema.get('type')
            
            if value_type == 'string':
                config[key] = env_value
            elif value_type == 'number':
                try:
                    config[key] = float(env_value)
                except ValueError:
                    logger.warning(f"Ungültiger Wert für {env_key}: {env_value}, erwartet: number")
            elif value_type == 'integer':
                try:
                    config[key] = int(env_value)
                except ValueError:
                    logger.warning(f"Ungültiger Wert für {env_key}: {env_value}, erwartet: integer")
            elif value_type == 'boolean':
                config[key] = env_value.lower() in ('true', 'yes', '1', 'y')
            elif value_type == 'array':
                config[key] = env_value.split(',')
            elif value_type == 'object':
                try:
                    config[key] = json.loads(env_value)
                except json.JSONDecodeError:
                    logger.warning(f"Ungültiger JSON-Wert für {env_key}: {env_value}")
        
        return config
    
    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe mehrere Konfigurationen zusammen.
        
        Args:
            *configs: Konfigurationen, die zusammengeführt werden sollen
            
        Returns:
            Dict mit der zusammengeführten Konfiguration
        """
        result = {}
        
        for config in configs:
            self._deep_update(result, config)
        
        return result


class ConfigSchema(Generic[T]):
    """
    Schema für die Validierung von Konfigurationen.
    
    Diese Klasse bietet eine typsichere Möglichkeit, Konfigurationen zu validieren
    und zu konvertieren.
    """
    
    def __init__(self, schema: Dict[str, Any], model_class: Type[T]):
        """
        Initialisiere das Schema.
        
        Args:
            schema: Schema für die Validierung
            model_class: Klasse für die Konvertierung
        """
        self.schema = schema
        self.model_class = model_class
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validiere eine Konfiguration.
        
        Args:
            config: Konfiguration, die validiert werden soll
            
        Returns:
            True, wenn die Konfiguration gültig ist, sonst False
            
        Raises:
            ConfigValidationError: Wenn die Konfiguration ungültig ist
        """
        errors = {}
        
        # Validiere die Konfiguration
        for key, value_schema in self.schema.items():
            if key not in config:
                if value_schema.get('required', False):
                    errors[key] = f"Pflichtfeld {key} fehlt"
                continue
            
            value = config[key]
            value_type = value_schema.get('type')
            
            if value_type and not self._check_type(value, value_type):
                errors[key] = f"Ungültiger Typ für {key}: {type(value).__name__}, erwartet: {value_type}"
                continue
            
            if 'enum' in value_schema and value not in value_schema['enum']:
                errors[key] = f"Ungültiger Wert für {key}: {value}, erwartet: {value_schema['enum']}"
                continue
            
            if 'min' in value_schema and value < value_schema['min']:
                errors[key] = f"Wert für {key} zu klein: {value}, Minimum: {value_schema['min']}"
                continue
            
            if 'max' in value_schema and value > value_schema['max']:
                errors[key] = f"Wert für {key} zu groß: {value}, Maximum: {value_schema['max']}"
                continue
            
            if 'pattern' in value_schema and not self._check_pattern(value, value_schema['pattern']):
                errors[key] = f"Wert für {key} entspricht nicht dem Muster: {value_schema['pattern']}"
                continue
            
            if 'properties' in value_schema and isinstance(value, dict):
                sub_errors = {}
                for sub_key, sub_schema in value_schema['properties'].items():
                    if sub_key not in value:
                        if sub_schema.get('required', False):
                            sub_errors[sub_key] = f"Pflichtfeld {sub_key} fehlt"
                        continue
                    
                    sub_value = value[sub_key]
                    sub_type = sub_schema.get('type')
                    
                    if sub_type and not self._check_type(sub_value, sub_type):
                        sub_errors[sub_key] = f"Ungültiger Typ für {sub_key}: {type(sub_value).__name__}, erwartet: {sub_type}"
                
                if sub_errors:
                    errors[key] = sub_errors
        
        if errors:
            raise ConfigValidationError("Konfiguration ist ungültig", errors)
        
        return True
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Überprüfe, ob ein Wert den erwarteten Typ hat.
        
        Args:
            value: Wert, der überprüft werden soll
            expected_type: Erwarteter Typ
            
        Returns:
            True, wenn der Wert den erwarteten Typ hat, sonst False
        """
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'null':
            return value is None
        else:
            return False
    
    def _check_pattern(self, value: str, pattern: str) -> bool:
        """
        Überprüfe, ob ein Wert einem Muster entspricht.
        
        Args:
            value: Wert, der überprüft werden soll
            pattern: Muster
            
        Returns:
            True, wenn der Wert dem Muster entspricht, sonst False
        """
        import re
        return bool(re.match(pattern, value))
    
    def to_model(self, config: Dict[str, Any]) -> T:
        """
        Konvertiere eine Konfiguration in ein Modell.
        
        Args:
            config: Konfiguration, die konvertiert werden soll
            
        Returns:
            Modell
            
        Raises:
            ConfigValidationError: Wenn die Konfiguration ungültig ist
        """
        self.validate(config)
        
        # Konvertiere die Konfiguration in ein Modell
        if hasattr(self.model_class, 'from_dict'):
            return self.model_class.from_dict(config)
        else:
            return self.model_class(**config)
    
    def from_model(self, model: T) -> Dict[str, Any]:
        """
        Konvertiere ein Modell in eine Konfiguration.
        
        Args:
            model: Modell, das konvertiert werden soll
            
        Returns:
            Dict mit der Konfiguration
        """
        # Konvertiere das Modell in eine Konfiguration
        if hasattr(model, 'to_dict'):
            return model.to_dict()
        else:
            return {k: v for k, v in model.__dict__.items() if not k.startswith('_')}


# Singleton-Instanz des Konfigurationsmanagers
_config_manager = None


def get_config_manager(config_dir: str = "config") -> ConfigManager:
    """
    Hole die Singleton-Instanz des Konfigurationsmanagers.
    
    Args:
        config_dir: Verzeichnis für Konfigurationsdateien
        
    Returns:
        Singleton-Instanz des Konfigurationsmanagers
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)
    
    return _config_manager