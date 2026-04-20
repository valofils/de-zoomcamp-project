#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT_DIR/01-docker-terraform/terraform"

if [[ -f "$ROOT_DIR/.env" ]]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

echo "=== GCP + Terraform Setup ==="
echo ""

# Step 1: Authenticate
echo "Step 1: Authenticating with GCP..."
gcloud auth application-default login --no-launch-browser

# Step 2: Set project
if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
    read -p "Enter your GCP Project ID: " GCP_PROJECT_ID
fi
gcloud config set project "$GCP_PROJECT_ID"
echo "✓ Project set to: $GCP_PROJECT_ID"

# Step 3: Enable APIs
echo ""
echo "Step 2: Enabling GCP APIs..."
gcloud services enable \
    storage.googleapis.com \
    bigquery.googleapis.com \
    iam.googleapis.com \
    --project "$GCP_PROJECT_ID"
echo "✓ APIs enabled"

# Step 4: Terraform
echo ""
echo "Step 3: Running Terraform..."

if [[ ! -f "$TF_DIR/terraform.tfvars" ]]; then
    sed "s/your-gcp-project-id/$GCP_PROJECT_ID/" \
        "$TF_DIR/terraform.tfvars.example" > "$TF_DIR/terraform.tfvars"
    echo "✓ Created terraform.tfvars"
fi

cd "$TF_DIR"
terraform init
terraform plan -out=tfplan

echo ""
read -p "Apply Terraform plan? (yes/no): " confirm
if [[ "$confirm" == "yes" ]]; then
    terraform apply tfplan
    echo ""
    echo "✅ GCP infrastructure provisioned!"
    terraform output
else
    echo "Skipped. Run 'terraform apply' manually in $TF_DIR"
fi