"""
Prompt-Optimierer für den Prompt MCP Server.

Dieses Modul bietet Funktionalität zur Optimierung von Benutzer-Prompts zu strukturierten Best-Practice-Prompts.
"""

import logging
import re
from typing import Dict, List, Optional, Any

from ..models.template import Template
from .template_manager import TemplateManager

# Erstelle Logger
logger = logging.getLogger(__name__)


class PromptOptimizer:
    """Prompt-Optimierer-Klasse."""

    def __init__(self, template_manager: TemplateManager):
        """
        Initialisiere den Prompt-Optimierer.

        Args:
            template_manager: Der Template-Manager
        """
        self.template_manager = template_manager

    async def optimize_prompt(
        self,
        user_prompt: str,
        template_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Optimiere einen Benutzer-Prompt zu einem strukturierten Best-Practice-Prompt.

        Args:
            user_prompt: Der zu optimierende Benutzer-Prompt
            template_id: Optionale Template-ID zur Verwendung
            context: Optionaler Kontext für das Template

        Returns:
            Der optimierte Prompt
        """
        try:
            # Verwende Standard-Template, wenn keines angegeben ist
            if not template_id:
                template_id = "default"
            
            # Hole Template
            template = self.template_manager.get_template(template_id)
            if not template:
                logger.warning(f"Template {template_id} nicht gefunden, verwende Rohprompt")
                return user_prompt
            
            # Bereite Kontext vor
            ctx = context or {}
            ctx["user_prompt"] = user_prompt
            
            # Analysiere Prompt-Struktur
            prompt_analysis = self._analyze_prompt(user_prompt)
            ctx.update(prompt_analysis)
            
            # Rendere Template
            optimized_prompt = self.template_manager.render_template(template_id, ctx)
            
            return optimized_prompt
        
        except Exception as e:
            logger.exception(f"Fehler bei der Prompt-Optimierung: {e}")
            # Fallback auf Rohprompt
            return user_prompt

    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analysiere die Struktur eines Prompts.

        Args:
            prompt: Der zu analysierende Prompt

        Returns:
            Ein Dictionary mit Analyseergebnissen
        """
        # Extrahiere Schlüsselkomponenten aus dem Prompt
        components = {
            "has_question": bool(re.search(r"\?", prompt)),
            "has_instruction": bool(re.search(r"\b(erstelle|generiere|schreibe|liste|erkläre|beschreibe|analysiere)\b", prompt.lower())),
            "has_context": len(prompt.split()) > 20,  # Einfache Heuristik: Längere Prompts enthalten wahrscheinlich Kontext
            "word_count": len(prompt.split()),
            "character_count": len(prompt),
        }
        
        # Identifiziere Prompt-Typ
        if components["has_instruction"]:
            components["prompt_type"] = "instruction"
        elif components["has_question"]:
            components["prompt_type"] = "question"
        else:
            components["prompt_type"] = "statement"
        
        # Identifiziere Themenbereich (einfache Heuristik)
        if re.search(r"\b(code|programmier|funktion|klasse|methode|api|entwickl|software)\b", prompt.lower()):
            components["domain"] = "programming"
        elif re.search(r"\b(text|schreib|artikel|blog|zusammenfass|essay|bericht)\b", prompt.lower()):
            components["domain"] = "writing"
        elif re.search(r"\b(analyse|daten|statistik|trend|vorhersage|modell)\b", prompt.lower()):
            components["domain"] = "analysis"
        else:
            components["domain"] = "general"
        
        return components

    async def generate_system_prompt(
        self,
        user_prompt: str,
        role: Optional[str] = None,
        style: Optional[str] = None,
        constraints: Optional[List[str]] = None,
    ) -> str:
        """
        Generiere einen System-Prompt basierend auf Benutzer-Prompt und Parametern.

        Args:
            user_prompt: Der Benutzer-Prompt
            role: Optionale Rolle für den Assistenten
            style: Optionaler Stil für die Antwort
            constraints: Optionale Einschränkungen für die Antwort

        Returns:
            Der generierte System-Prompt
        """
        try:
            # Analysiere Prompt
            prompt_analysis = self._analyze_prompt(user_prompt)
            
            # Wähle passende Rolle basierend auf Domain, wenn keine angegeben ist
            if not role:
                if prompt_analysis["domain"] == "programming":
                    role = "erfahrener Softwareentwickler"
                elif prompt_analysis["domain"] == "writing":
                    role = "professioneller Texter"
                elif prompt_analysis["domain"] == "analysis":
                    role = "Datenanalyst"
                else:
                    role = "hilfreicher Assistent"
            
            # Erstelle System-Prompt
            system_prompt = f"Du bist ein {role}. "
            
            # Füge Stil hinzu, wenn angegeben
            if style:
                system_prompt += f"Antworte in einem {style} Stil. "
            
            # Füge Einschränkungen hinzu, wenn angegeben
            if constraints:
                system_prompt += "Beachte folgende Einschränkungen: "
                for constraint in constraints:
                    system_prompt += f"- {constraint}\n"
            
            return system_prompt
        
        except Exception as e:
            logger.exception(f"Fehler bei der System-Prompt-Generierung: {e}")
            # Fallback auf Standard-System-Prompt
            return "Du bist ein hilfreicher Assistent."