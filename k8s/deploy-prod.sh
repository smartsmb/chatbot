#!/bin/bash

# k8s/deploy-prod.sh - Production deployment with PostgreSQL/RDS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="chatbot"
ENVIRONMENT="production"

echo -e "${GREEN}Starting PRODUCTION deployment with PostgreSQL/RDS${NC}"

# Check if production config is updated
echo -e "${RED}IMPORTANT: Ensure config-backend-prod.yaml is updated with your RDS configuration!${NC}"
echo -e "${RED}IMPORTANT: Ensure secret-backend.yaml is updated with your production secrets!${NC}"
read -p "Press Enter to continue after updating production configuration..."

# Create namespace
kubectl apply -f namespace.yaml

# Create service accounts
kubectl apply -f service-accounts.yaml

# Create secrets
kubectl apply -f secret-backend.yaml

# Create production config (PostgreSQL/RDS)
kubectl apply -f config-backend-prod.yaml

# Deploy backend
kubectl apply -f deployment-backend.yaml
kubectl apply -f service-backend.yaml

# Deploy frontend
kubectl apply -f deployment-frontend.yaml
kubectl apply -f service-frontend.yaml

# Deploy additional production resources
kubectl apply -f hpa.yaml
kubectl apply -f pdb.yaml
kubectl apply -f network-policy.yaml

# Deploy ingress (update with your domain first)
echo -e "${RED}IMPORTANT: Update ingress.yaml with your domain and certificate ARN!${NC}"
read -p "Press Enter to continue after updating ingress configuration..."
kubectl apply -f ingress.yaml

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-backend -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-frontend -n $NAMESPACE

echo -e "${GREEN}Production deployment completed!${NC}"
echo -e "${YELLOW}Database: PostgreSQL/RDS${NC}"
echo -e "${YELLOW}Check your ALB endpoint for external access${NC}"
