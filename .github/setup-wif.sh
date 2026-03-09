#!/usr/bin/env bash
# One-time setup: Workload Identity Federation for GitHub Actions → GCP
# Run this locally with gcloud authenticated as a project owner.
#
# After running, add these GitHub repository secrets:
#   WIF_PROVIDER   → printed at the end
#   WIF_SERVICE_ACCOUNT → printed at the end

set -euo pipefail

PROJECT_ID="student-marketing-operations"
SA_NAME="github-actions-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"
GITHUB_REPO="bharat-sketch/smo-monolith"

echo "=== 1. Create service account ==="
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="GitHub Actions Deploy" \
  --project="$PROJECT_ID" 2>/dev/null || echo "  (already exists)"

echo "=== 2. Grant roles to service account ==="
for ROLE in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser roles/cloudsql.client; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE" \
    --quiet
done

echo "=== 3. Create Workload Identity Pool ==="
gcloud iam workload-identity-pools create "$POOL_NAME" \
  --location="global" \
  --display-name="GitHub Actions" \
  --project="$PROJECT_ID" 2>/dev/null || echo "  (already exists)"

echo "=== 4. Create OIDC Provider ==="
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
  --location="global" \
  --workload-identity-pool="$POOL_NAME" \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='${GITHUB_REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project="$PROJECT_ID" 2>/dev/null || echo "  (already exists)"

echo "=== 5. Allow GitHub repo to impersonate SA ==="
POOL_ID=$(gcloud iam workload-identity-pools describe "$POOL_NAME" \
  --location="global" --project="$PROJECT_ID" --format="value(name)")

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  --project="$PROJECT_ID"

echo ""
echo "=========================================="
echo "Setup complete! Add these as GitHub secrets:"
echo "=========================================="
echo ""

WIF_PROVIDER=$(gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
  --location="global" \
  --workload-identity-pool="$POOL_NAME" \
  --project="$PROJECT_ID" \
  --format="value(name)")

echo "WIF_PROVIDER=${WIF_PROVIDER}"
echo "WIF_SERVICE_ACCOUNT=${SA_EMAIL}"
echo ""
echo "Go to: https://github.com/${GITHUB_REPO}/settings/secrets/actions"
