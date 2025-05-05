# Entwickler-Prompt: n8n Workflow-Module für GitHub-GitLab-OpenProject Integration

## Projektübersicht

Wir benötigen einen umfassenden n8n-basierten Workflow zur Integration und Synchronisation zwischen lokalem GitLab, GitHub und OpenProject. Dieses System soll die Verwaltung von 30+ Repositories ermöglichen, die in Produktgruppen organisiert sind, mit verschiedenen spezialisierten Roadmaps.

## Technische Anforderungen

1. **Plattformen**:
   - Lokaler GitLab-Server (primäre Entwicklungsplattform)
   - GitHub (für Community-Interaktion und öffentliche Releases)
   - OpenProject (zentrales Projektmanagement)

2. **n8n als Integrationsplattform**:
   - Modularer Aufbau für bessere Wartbarkeit
   - Einsatz von Webhooks, Polling und zeitgesteuerten Triggers
   - Bidirektionale Synchronisation zwischen Systemen

## Zu entwickelnde Module

Entwickeln Sie die folgenden Module als separate n8n-Workflows, die miteinander interagieren können:

### 1. GitLab-OpenProject-Basis-Synchronisation

- **Funktionsumfang**:
  - Erfassung und Synchronisation von GitLab-Issues zu OpenProject-Work-Packages
  - Bidirektionale Status-Synchronisation
  - Erfassung von Merge Requests und deren Status
  - Mapping von GitLab-Meilensteinen zu OpenProject-Phasen
  - Kommentar-Synchronisation zwischen beiden Systemen

- **Technische Anforderungen**:
  - GitLab-Webhooks als Trigger
  - Implementierung von ID-Mapping zwischen Systemen
  - Vermeidung von Synchronisationsschleifen
  - Unterstützung für benutzerdefinierte Felder in OpenProject

### 2. GitHub-GitLab-Community-Bridge

- **Funktionsumfang**:
  - Erfassung relevanter GitHub-Issues und Übertragung nach GitLab
  - Synchronisation von GitLab-Releases zu GitHub
  - Tracking von GitHub-Community-Metriken (Stars, Forks, Issues)
  - Bidirektionale Status-Updates zwischen GitHub und GitLab

- **Technische Anforderungen**:
  - GitHub-Webhooks als Trigger
  - Selektive Synchronisation basierend auf konfigurierbaren Regeln
  - Unterstützung für Release-Tags und Assets
  - Erfassung von Community-Statistiken

### 3. Dokumentations-Analyse und Roadmap-Generierung

- **Funktionsumfang**:
  - Extraktion strukturierter Informationen aus GitLab-Dokumentationen
  - Generierung verschiedener Roadmap-Typen (Entwicklung, Strategie, Finanzierung)
  - Repository- und Produkt-übergreifende Aggregation
  - Integration in OpenProject-Roadmaps

- **Technische Anforderungen**:
  - GitLab API für Zugriff auf Dokumentationen
  - Parser für Markdown/Wiki-Formate
  - Templating-System für verschiedene Roadmap-Typen
  - Zeitplan-basierte Ausführung (wöchentlich)

### 4. Release-Management-Workflow

- **Funktionsumfang**:
  - Automatisierung des Release-Prozesses von GitLab zu GitHub
  - Erstellung von Release-Notes basierend auf Issues und Merge Requests
  - Aktualisierung von Roadmaps und Status in OpenProject
  - Community-Benachrichtigungen für neue Releases

- **Technische Anforderungen**:
  - Trigger durch GitLab-Tags oder Meilenstein-Abschluss
  - Release-Asset-Verwaltung
  - Changelog-Generierung
  - Benachrichtigungssystem

### 5. Reporting und Überwachung

- **Funktionsumfang**:
  - Sammlung von Fortschrittsdaten aus allen Systemen
  - Berechnung von KPIs und Projektmetriken
  - Erstellung von Status-Berichten
  - Frühwarnsystem für Abweichungen vom Plan

- **Technische Anforderungen**:
  - Daten-Aggregation aus allen Systemen
  - Berechnungslogik für Projektmetriken
  - Berichts-Templating
  - Alert-System bei Abweichungen

## Architekturelle Anforderungen

1. **Modularer Aufbau**:
   - Jedes Modul sollte eigenständig funktionsfähig sein
   - Klare Schnittstellen zwischen den Modulen
   - Wiederverwendbare Komponenten für ähnliche Funktionen

2. **Konfigurierbarkeit**:
   - Alle System-URLs und Zugangsdaten als Umgebungsvariablen
   - Konfigurierbare Mapping-Regeln zwischen Systemen
   - Anpassbare Synchronisationsintervalle

3. **Fehlerbehandlung**:
   - Robustes Logging aller Operationen
   - Wiederholungslogik bei temporären Fehlern
   - Benachrichtigungen bei kritischen Fehlern
   - Vermeidung von Datenverlust bei Ausfällen

4. **Skalierbarkeit**:
   - Effiziente Verarbeitung von 30+ Repositories
   - Batching von API-Aufrufen wo möglich
   - Inkrementelle Synchronisation um Ressourcen zu schonen

## Technische Spezifikationen

1. **API-Zugriff**:
   - GitLab: Lokaler Server (keine API-Limits)
   - GitHub: OAuth-Authentifizierung mit minimalen notwendigen Scopes
   - OpenProject: API-Token mit entsprechenden Berechtigungen

2. **Datenstruktur**:
   - Standardisiertes Mapping-Schema zwischen Systemen
   - Speicherung von Referenz-IDs zur Nachverfolgung
   - Benutzerdefinierte Felder für systemspezifische Metadaten

3. **n8n-spezifische Anforderungen**:
   - Nutzung von Subfunktionen für bessere Struktur
   - Einsatz von Data Mapping mit JSONata für komplexe Transformationen
   - Implementierung von Fehlerwarteschlangen für robuste Ausführung
   - Dokumentation aller Workflow-Entscheidungen

## Lieferumfang

Für jedes Modul erwarten wir:

1. Funktionsfähigen n8n-Workflow als JSON
2. Dokumentation der Konfigurationsparameter
3. Installationsanleitung
4. Testfälle zur Validierung
5. Beispielkonfigurationen für typische Anwendungsfälle

## Zeitplan und Prioritäten

Entwickeln Sie die Module in folgender Reihenfolge:

1. GitLab-OpenProject-Basis-Synchronisation (höchste Priorität)
2. GitHub-GitLab-Community-Bridge
3. Release-Management-Workflow
4. Dokumentations-Analyse und Roadmap-Generierung
5. Reporting und Überwachung

## Erwartete Herausforderungen

1. Komplexe bidirektionale Synchronisation ohne Schleifen
2. Effiziente Verarbeitung großer Datenmengen
3. Strukturierte Informationsextraktion aus Dokumentationen
4. Konsistente Statusverfolgung über mehrere Systeme

## Kontaktperson für Rückfragen

Bei technischen Fragen oder Unklarheiten zur Anforderungsspezifikation wenden Sie sich an den Projektmanager.

---

Entwickeln Sie diese n8n-Workflow-Module mit höchstem Fokus auf Zuverlässigkeit, Wartbarkeit und Effizienz. Die Workflows sollen eine nahtlose Integration zwischen GitLab, GitHub und OpenProject ermöglichen und dabei den spezifischen Anforderungen unserer Repository- und Produkt-Struktur gerecht werden.
