# EKS Deployment for Chatbot Application

This directory contains Kubernetes manifests for deploying the chatbot application on Amazon EKS.

## Prerequisites

1. **EKS Cluster**: An EKS cluster must be running
2. **AWS Load Balancer Controller**: Installed in your cluster
3. **kubectl**: Configured to connect to your EKS cluster
4. **Docker Images**: Built and pushed to ECR
5. **RDS Database**: PostgreSQL database for production (optional, can use SQLite for testing)

## Environment-Driven Configuration

This deployment uses environment-driven configuration with safe defaults:

### **Default Behavior (No Environment Set)**

- **Database**: SQLite (safe default for local/dev)
- **CORS**: Includes localhost for development
- **Logging**: DEBUG level
- **Resources**: Minimal for development

### **Environment-Specific Configurations**

#### Development (`ENVIRONMENT=development`)

- **Database**: SQLite (`sqlite:///./chatbot.db`)
- **CORS**: `http://localhost:5173,http://localhost:3000,http://localhost:8080`
- **Logging**: DEBUG level
- **File**: `config-backend-dev.yaml`

#### Production (`ENVIRONMENT=production`)

- **Database**: PostgreSQL/RDS (requires configuration)
- **CORS**: Production domains only
- **Logging**: WARNING level
- **File**: `config-backend-prod.yaml`

### **Configuration Priority**

1. **Environment Variables** (highest priority)
2. **Environment-specific ConfigMap** (e.g., `config-backend-prod.yaml`)
3. **Base ConfigMap** (`config-backend.yaml`)
4. **Application Defaults** (SQLite fallback)

## Required AWS Resources

- EKS Cluster
- ECR repositories for backend and frontend images
- RDS PostgreSQL instance (recommended for production)
- SSL Certificate in ACM (for HTTPS)
- Security Groups
- Subnets (public/private)

## Configuration

Before deploying, update the following files with your actual values:

### 1. Image References

Update the image references in:

- `deployment-backend.yaml`
- `deployment-frontend.yaml`

Replace:

- `<ACCOUNT_ID>` with your AWS account ID
- `<REGION>` with your AWS region

### 2. Secrets

Update `secret-backend.yaml` with:

- Your actual OpenAI API key
- Strong JWT secret
- Database credentials (if not using IAM)

### 3. Configuration

Update `config-backend.yaml` with:

- Your RDS database URL
- Your actual domain for CORS origins
- Environment-specific settings

### 4. Ingress

Update `ingress.yaml` with:

- Your actual domain name
- Your SSL certificate ARN
- Your security group IDs
- Your subnet IDs

## Deployment

### Environment-Specific Deployment Scripts

#### Development (SQLite - Safe Default)

```bash
# Quick development deployment with SQLite
./deploy-dev.sh
```

#### Production (PostgreSQL/RDS)

```bash
# Production deployment with PostgreSQL/RDS
./deploy-prod.sh
```

#### Environment-Aware Deployment

```bash
# Set required environment variables
export AWS_ACCOUNT_ID="123456789012"
export AWS_REGION="us-west-2"
export EKS_CLUSTER_NAME="your-cluster-name"
export ENVIRONMENT="production"  # or "development", "staging"

# Run the environment-aware deployment script
./deploy.sh
```

### Manual Deployment

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create service accounts
kubectl apply -f service-accounts.yaml

# Create secrets (update first!)
kubectl apply -f secret-backend.yaml

# Create config map (update first!)
kubectl apply -f config-backend.yaml

# Deploy backend
kubectl apply -f deployment-backend.yaml
kubectl apply -f service-backend.yaml

# Deploy frontend
kubectl apply -f deployment-frontend.yaml
kubectl apply -f service-frontend.yaml

# Deploy additional resources
kubectl apply -f hpa.yaml
kubectl apply -f pdb.yaml
kubectl apply -f network-policy.yaml
kubectl apply -f ingress.yaml
```

## Monitoring

### Check Pod Status

```bash
kubectl get pods -n chatbot
```

### Check Services

```bash
kubectl get services -n chatbot
```

### Check Ingress

```bash
kubectl get ingress -n chatbot
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/chatbot-backend -n chatbot

# Frontend logs
kubectl logs -f deployment/chatbot-frontend -n chatbot
```

### Scale Manually

```bash
# Scale backend
kubectl scale deployment chatbot-backend --replicas=3 -n chatbot

# Scale frontend
kubectl scale deployment chatbot-frontend --replicas=3 -n chatbot
```

## Security Features

- **Pod Security Context**: Non-root user, read-only filesystem
- **Network Policies**: Restrictive ingress/egress rules
- **Resource Limits**: CPU and memory limits on all containers
- **Secrets Management**: Sensitive data stored in Kubernetes secrets
- **Service Accounts**: Dedicated service accounts for each component

## High Availability Features

- **Multiple Replicas**: Minimum 2 replicas for each service
- **Horizontal Pod Autoscaler**: Automatic scaling based on CPU/memory
- **Pod Disruption Budgets**: Ensure minimum availability during updates
- **Health Checks**: Readiness and liveness probes

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Verify ECR permissions and image tags
2. **Pod Startup Failures**: Check logs and resource constraints
3. **Service Connectivity**: Verify service selectors and ports
4. **Ingress Issues**: Check ALB configuration and security groups

### Useful Commands

```bash
# Describe resources for debugging
kubectl describe pod <pod-name> -n chatbot
kubectl describe service <service-name> -n chatbot
kubectl describe ingress <ingress-name> -n chatbot

# Check events
kubectl get events -n chatbot --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward service/chatbot-backend-svc 8000:80 -n chatbot
kubectl port-forward service/chatbot-frontend-svc 3000:80 -n chatbot
```

## Cleanup

To remove all resources:

```bash
kubectl delete namespace chatbot
```

## Production Considerations

1. **Database**: Use RDS PostgreSQL instead of SQLite
2. **Monitoring**: Set up CloudWatch Container Insights
3. **Logging**: Configure Fluent Bit for log aggregation
4. **Backup**: Regular database backups
5. **Updates**: Use rolling updates for zero-downtime deployments
6. **Security**: Regular security scanning and updates
