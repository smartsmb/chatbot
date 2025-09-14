#!/bin/bash

# k8s/deploy-dev.sh - Development deployment with SQLite (safe default)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="chatbot"
ENVIRONMENT="development"

echo -e "${GREEN}Starting DEVELOPMENT deployment with SQLite (safe default)${NC}"

# Create namespace
kubectl apply -f namespace.yaml

# Create service accounts
kubectl apply -f service-accounts.yaml

# Create secrets (update with your actual values)
kubectl apply -f secret-backend.yaml

# Create development config (SQLite)
kubectl apply -f config-backend-dev.yaml

# Deploy backend
kubectl apply -f deployment-backend.yaml
kubectl apply -f service-backend.yaml

# Deploy frontend
kubectl apply -f deployment-frontend.yaml
kubectl apply -f service-frontend.yaml

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-backend -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-frontend -n $NAMESPACE

echo -e "${GREEN}Development deployment completed!${NC}"
echo -e "${YELLOW}Database: SQLite (safe default)${NC}"
echo -e "${YELLOW}To access the application:${NC}"
echo "kubectl port-forward service/chatbot-frontend-svc 3000:80 -n $NAMESPACE"
echo "kubectl port-forward service/chatbot-backend-svc 8000:80 -n $NAMESPACE"
