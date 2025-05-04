<div align="center">
  <img src="./docs/static/img/logo.png" alt="Logo" width="200">
  <h1>EcoSphere Network: n8n Workflow Integrations</h1>
  <p>Modulare Automatisierung von AFFiNE, AppFlowy, GitHub/GitLab, OpenProject und OpenHands mit n8n.</p>

  [![Contributors][contributors-shield]][contributors-url]
  [![Stars][stars-shield]][stars-url]
  [![Coverage][coverage-shield]][coverage-url]
  [![MIT License][license-shield]][license-url]
  <br/>
  [![Discord][discord-shield]][discord-url]
  [![Documentation][docs-shield]][docs-url]
  [![Project Credits][credits-shield]][credits-url]

  [Start Documentation](https://github.com/EcoSphereNetwork/ESN_Repo-Template/blob/main/docs/README.md) •
  [Report Bug](https://github.com/EcoSphereNetwork/ESN_Repo-Template/issues) •
  [Request Feature](https://github.com/EcoSphereNetwork/ESN_Repo-Template/issues)
</div>

## 📋 Table of Contents
- [About](#-about)
- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Workflows](#-workflows)
- [Development](#-development)
- [Deployment](#-deployment)
- [Support](#-support)
- [License](#-license)

## 🎯 About
Dieses Repository enthält ein modulares Setup zur Einrichtung und Erweiterung von **n8n-Workflows** innerhalb des EcoSphere Network. Es ermöglicht die Automatisierung und Synchronisierung zwischen:

- 🧠 AFFiNE / AppFlowy (Wissensmanagement)
- 🛠️ GitHub / GitLab (Code-Management)
- 📈 OpenProject (Projektmanagement)
- 🤖 OpenHands (KI-gestützte Issue-Lösungen)

## ✨ Key Features
- 🔄 Vollständige Synchronisation von Dokumenten und Issues zwischen Tools
- 🧩 Modulare Struktur für einfache Erweiterung und Wiederverwendbarkeit
- 🐳 Docker-basierte lokale Installation
- 📡 Webhook-Unterstützung für Live-Updates
- 🛡️ Integration von Sicherheits- und Qualitätschecks

## 🚀 Getting Started

### Prerequisites
- Python 3.6+
- Docker + Docker Compose
- Gültige API-Tokens für alle Tools
- `pip install requests`

### Installation

```bash
git clone git@github.com:EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
cp .env-template .env  # .env mit API-Schlüsseln ausfüllen

python n8n_setup_main.py --install --env-file .env
