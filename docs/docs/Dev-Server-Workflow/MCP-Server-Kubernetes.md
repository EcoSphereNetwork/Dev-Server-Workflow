# MCP-Server-Kubernetes-Deployment

Diese Dokumentation beschreibt, wie die MCP-Server in einer Kubernetes-Umgebung bereitgestellt werden können.

## Übersicht

Die MCP-Server können in einer Kubernetes-Umgebung bereitgestellt werden, um Skalierbarkeit, Hochverfügbarkeit und einfache Verwaltung zu ermöglichen. Diese Dokumentation beschreibt die Schritte zur Bereitstellung der MCP-Server in Kubernetes.

## Voraussetzungen

- Kubernetes-Cluster (z.B. Minikube, Kind, EKS, GKE, AKS)
- kubectl (konfiguriert für den Zugriff auf den Cluster)
- Docker-Registry mit den MCP-Server-Images

## Architektur

Die Kubernetes-Bereitstellung der MCP-Server besteht aus den folgenden Komponenten:

1. **Deployments**: Für jeden MCP-Server gibt es ein Deployment, das die Container-Spezifikation und die Replikationseinstellungen enthält.
2. **Services**: Für jeden MCP-Server gibt es einen Service, der den Zugriff auf den Server ermöglicht.
3. **ConfigMaps**: Für die Konfiguration der MCP-Server.
4. **Secrets**: Für sensible Informationen wie Passwörter und Tokens.
5. **Volumes**: Für die Persistenz von Daten.

## Bereitstellung

### Automatische Bereitstellung

Die einfachste Methode zur Bereitstellung der MCP-Server in Kubernetes ist die Verwendung des Bereitstellungsskripts:

```bash
cd /workspace/Dev-Server-Workflow/kubernetes
./deploy-mcp-servers.sh
```

Das Skript führt die folgenden Schritte aus:

1. Erstellt den Namespace `mcp-servers`
2. Erstellt ConfigMaps und Secrets für die Konfiguration
3. Wendet die Kubernetes-Manifeste an
4. Wartet, bis alle Deployments bereit sind
5. Zeigt Informationen zu den Services an

### Manuelle Bereitstellung

Wenn Sie die MCP-Server manuell bereitstellen möchten, folgen Sie diesen Schritten:

1. Erstellen Sie den Namespace:

```bash
kubectl create namespace mcp-servers
```

2. Erstellen Sie ConfigMaps und Secrets:

```bash
kubectl create configmap mcp-config --namespace mcp-servers --from-file=../docker-mcp-servers/.env.example
kubectl create secret generic mcp-secrets --namespace mcp-servers --from-literal=redis-password=redis_password --from-literal=github-token=YOUR_GITHUB_TOKEN
```

3. Wenden Sie die Kubernetes-Manifeste an:

```bash
kubectl apply -f manifests/ --namespace mcp-servers
```

## Zugriff auf die MCP-Server

Nach der Bereitstellung können Sie auf die MCP-Server über die Services zugreifen. Der MCP-Inspector ist als LoadBalancer-Service konfiguriert und kann über die externe IP-Adresse erreicht werden:

```bash
kubectl get service mcp-inspector --namespace mcp-servers
```

Wenn Sie Minikube verwenden, können Sie den MCP-Inspector mit dem folgenden Befehl erreichen:

```bash
minikube service mcp-inspector --namespace mcp-servers
```

Die anderen MCP-Server sind als ClusterIP-Services konfiguriert und können nur innerhalb des Clusters erreicht werden. Sie können Port-Forwarding verwenden, um auf sie zuzugreifen:

```bash
kubectl port-forward service/filesystem-mcp 3001:3001 --namespace mcp-servers
```

## Skalierung

Sie können die MCP-Server skalieren, indem Sie die Anzahl der Replikate in den Deployments ändern:

```bash
kubectl scale deployment filesystem-mcp --replicas=3 --namespace mcp-servers
```

## Überwachung

Sie können die MCP-Server mit den Standard-Kubernetes-Tools überwachen:

```bash
kubectl get pods --namespace mcp-servers
kubectl logs deployment/filesystem-mcp --namespace mcp-servers
kubectl describe deployment filesystem-mcp --namespace mcp-servers
```

Für eine umfassendere Überwachung empfehlen wir die Verwendung von Prometheus und Grafana, wie in der [MCP-Server-Überwachung](MCP-Server-Monitoring.md) beschrieben.

## Fehlerbehebung

Wenn Sie Probleme mit der Kubernetes-Bereitstellung haben:

1. Überprüfen Sie den Status der Pods:
   ```bash
   kubectl get pods --namespace mcp-servers
   ```

2. Überprüfen Sie die Logs der Pods:
   ```bash
   kubectl logs pod/POD_NAME --namespace mcp-servers
   ```

3. Beschreiben Sie die Pods, um weitere Informationen zu erhalten:
   ```bash
   kubectl describe pod/POD_NAME --namespace mcp-servers
   ```

## Sicherheit

Die MCP-Server-Deployments sind mit Sicherheitseinstellungen konfiguriert, um die Sicherheit zu verbessern:

- Die Container laufen ohne Root-Rechte
- Die Container haben eingeschränkte Capabilities
- Die Container haben keine Privilegien-Eskalation

Für eine Produktionsumgebung empfehlen wir die Verwendung von Network Policies, Pod Security Policies und RBAC, um die Sicherheit weiter zu verbessern.

## Referenzen

- [Kubernetes-Dokumentation](https://kubernetes.io/docs/home/)
- [Minikube-Dokumentation](https://minikube.sigs.k8s.io/docs/)
- [Kind-Dokumentation](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [MCP-Server-Überwachung](MCP-Server-Monitoring.md)