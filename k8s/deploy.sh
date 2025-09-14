#!/bin/bash

# k8s/deploy.sh - EKS Deployment Script for Chatbot Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="chatbot"
REGION="${AWS_REGION:-us-west-2}"
ACCOUNT_ID="${AWS_ACCOUNT_ID}"
CLUSTER_NAME="${EKS_CLUSTER_NAME:-chatbot-cluster}"
ENVIRONMENT="${ENVIRONMENT:-development}"  # development, staging, production

echo -e "${GREEN}Starting EKS deployment for Chatbot Application${NC}"
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"

# Check if required environment variables are set
if [ -z "$ACCOUNT_ID" ]; then
    echo -e "${RED}Error: AWS_ACCOUNT_ID environment variable is not set${NC}"
    exit 1
fi

if [ -z "$EKS_CLUSTER_NAME" ]; then
    echo -e "${YELLOW}Warning: EKS_CLUSTER_NAME not set, using default: $CLUSTER_NAME${NC}"
fi

# Update image references in deployment files
echo -e "${YELLOW}Updating image references...${NC}"
sed -i.bak "s/<ACCOUNT_ID>/$ACCOUNT_ID/g" deployment-backend.yaml
sed -i.bak "s/<ACCOUNT_ID>/$ACCOUNT_ID/g" deployment-frontend.yaml
sed -i.bak "s/<REGION>/$REGION/g" deployment-backend.yaml
sed -i.bak "s/<REGION>/$REGION/g" deployment-frontend.yaml

# Verify kubectl is configured for the correct cluster
echo -e "${YELLOW}Verifying kubectl configuration...${NC}"
kubectl cluster-info

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl apply -f namespace.yaml

# Create service accounts
echo -e "${YELLOW}Creating service accounts...${NC}"
kubectl apply -f service-accounts.yaml

# Create secrets
echo -e "${YELLOW}Creating secrets...${NC}"
echo -e "${RED}IMPORTANT: Update secret-backend.yaml with your actual secrets before proceeding!${NC}"
read -p "Press Enter to continue after updating secrets..."

kubectl apply -f secret-backend.yaml

# Create config map based on environment
echo -e "${YELLOW}Creating config map for $ENVIRONMENT environment...${NC}"

if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}Using production configuration (PostgreSQL/RDS)${NC}"
    echo -e "${RED}IMPORTANT: Update config-backend-prod.yaml with your actual RDS configuration!${NC}"
    read -p "Press Enter to continue after updating production configuration..."
    kubectl apply -f config-backend-prod.yaml
    # Update the deployment to use production config
    kubectl patch deployment chatbot-backend -n $NAMESPACE -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"DATABASE_URL","valueFrom":{"configMapKeyRef":{"name":"chatbot-backend-config-prod","key":"DATABASE_URL"}}}]}]}}}}'
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo -e "${YELLOW}Using staging configuration (PostgreSQL)${NC}"
    echo -e "${RED}IMPORTANT: Update config-backend-prod.yaml with your staging database configuration!${NC}"
    read -p "Press Enter to continue after updating staging configuration..."
    kubectl apply -f config-backend-prod.yaml
    # Update the deployment to use staging config
    kubectl patch deployment chatbot-backend -n $NAMESPACE -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"DATABASE_URL","valueFrom":{"configMapKeyRef":{"name":"chatbot-backend-config-prod","key":"DATABASE_URL"}}}]}]}}}}'
else
    echo -e "${YELLOW}Using development configuration (SQLite - safe default)${NC}"
    kubectl apply -f config-backend-dev.yaml
    # Update the deployment to use dev config
    kubectl patch deployment chatbot-backend -n $NAMESPACE -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"DATABASE_URL","valueFrom":{"configMapKeyRef":{"name":"chatbot-backend-config-dev","key":"DATABASE_URL"}}}]}]}}}}'
fi

# Apply the base config as fallback
kubectl apply -f config-backend.yaml

# Deploy backend
echo -e "${YELLOW}Deploying backend...${NC}"
kubectl apply -f deployment-backend.yaml
kubectl apply -f service-backend.yaml

# Deploy frontend
echo -e "${YELLOW}Deploying frontend...${NC}"
kubectl apply -f deployment-frontend.yaml
kubectl apply -f service-frontend.yaml

# Deploy HPA
echo -e "${YELLOW}Deploying Horizontal Pod Autoscaler...${NC}"
kubectl apply -f hpa.yaml

# Deploy PDB
echo -e "${YELLOW}Deploying Pod Disruption Budgets...${NC}"
kubectl apply -f pdb.yaml

# Deploy Network Policy
echo -e "${YELLOW}Deploying Network Policy...${NC}"
kubectl apply -f network-policy.yaml

# Deploy Ingress
echo -e "${YELLOW}Deploying Ingress...${NC}"
echo -e "${RED}IMPORTANT: Update ingress.yaml with your actual domain and certificate ARN before proceeding!${NC}"
read -p "Press Enter to continue after updating ingress configuration..."

kubectl apply -f ingress.yaml

# Wait for deployments to be ready
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-backend -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/chatbot-frontend -n $NAMESPACE

# Show status
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Checking pod status:${NC}"
kubectl get pods -n $NAMESPACE

echo -e "${YELLOW}Checking services:${NC}"
kubectl get services -n $NAMESPACE

echo -e "${YELLOW}Checking ingress:${NC}"
kubectl get ingress -n $NAMESPACE

echo -e "${GREEN}Deployment successful!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your DNS to point to the ALB endpoint"
echo "2. Verify SSL certificate is properly configured"
echo "3. Test the application endpoints"
echo "4. Monitor logs: kubectl logs -f deployment/chatbot-backend -n $NAMESPACE"

