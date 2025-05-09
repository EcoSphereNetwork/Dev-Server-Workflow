#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Script to deploy MCP servers to Kubernetes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display messages
log() {
    log_info "${GREEN}[INFO]${NC} $1"
}

warn() {
    log_info "${YELLOW}[WARN]${NC} $1"
}

error() {
    log_info "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    error "kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Check if a Kubernetes cluster is available
if ! kubectl cluster-info &> /dev/null; then
    error "No Kubernetes cluster is available. Please configure kubectl to connect to a cluster and try again."
    exit 1
fi

# Create the mcp-servers namespace if it doesn't exist
if ! kubectl get namespace mcp-servers &> /dev/null; then
    log "Creating mcp-servers namespace..."
    kubectl create namespace mcp-servers
fi

# Create a ConfigMap for the MCP server configuration
log "Creating ConfigMap for MCP server configuration..."
kubectl create configmap mcp-config --namespace mcp-servers --from-file=../docker-mcp-servers/.env.example --dry-run=client -o yaml | kubectl apply -f -

# Create a Secret for sensitive information
log "Creating Secret for sensitive information..."
kubectl create secret generic mcp-secrets --namespace mcp-servers --from-literal=redis-password=redis_password --from-literal=github-token=${GITHUB_TOKEN:-""} --dry-run=client -o yaml | kubectl apply -f -

# Apply the Kubernetes manifests
log "Applying Kubernetes manifests..."
kubectl apply -f manifests/ --namespace mcp-servers

# Wait for the deployments to be ready
log "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/redis-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/filesystem-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/desktop-commander-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/sequential-thinking-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/github-chat-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/github-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/puppeteer-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/basic-memory-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/wikipedia-mcp
kubectl wait --for=condition=available --timeout=300s --namespace mcp-servers deployment/mcp-inspector

# Get the service information
log "MCP servers have been deployed to Kubernetes."
log "Service information:"
kubectl get services --namespace mcp-servers

log "You can access the MCP Inspector UI at: http://$(kubectl get service mcp-inspector --namespace mcp-servers -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8080"
log "If you're using Minikube, you can access the MCP Inspector UI with: minikube service mcp-inspector --namespace mcp-servers"

exit 0