# ============================================================
# MicroTask Helm Rollback Demonstration
# Safe, reversible change: bump api.logLevel from INFO to DEBUG,
# then roll back to restore INFO.
#
# Prerequisites:
#   - kubectl context is set to microtask-eks-dev
#   - helm release "microtask" exists in namespace "microtask"
#
# Run from the repository root on PowerShell.
# ============================================================

# ── Step 1: Record current revision ──────────────────────────────────────────
Write-Host "`n=== Current Helm history ===" -ForegroundColor Cyan
helm history microtask -n microtask

# ── Step 2: Apply a harmless reversible change ────────────────────────────────
# We change api.logLevel to DEBUG. This triggers a rolling update of the API
# pod only. No database, PVC, or MySQL resources are touched.
Write-Host "`n=== Upgrading: setting api.logLevel=DEBUG ===" -ForegroundColor Yellow
helm upgrade microtask .\helm\microtask `
  --namespace microtask `
  -f .\helm\microtask\values-eks-dev.yaml `
  --set api.logLevel=DEBUG `
  --atomic `
  --timeout 3m

# --atomic: if the upgrade fails, Helm automatically rolls back.
# --timeout 3m: wait up to 3 minutes for pods to become ready.

# ── Step 3: Verify new revision ───────────────────────────────────────────────
Write-Host "`n=== Helm history after upgrade ===" -ForegroundColor Cyan
helm history microtask -n microtask

Write-Host "`n=== Pod status ===" -ForegroundColor Cyan
kubectl get pods -n microtask

# ── Step 4: Roll back to previous revision ────────────────────────────────────
Write-Host "`n=== Rolling back to previous revision ===" -ForegroundColor Yellow
helm rollback microtask -n microtask

# ── Step 5: Verify rollback ───────────────────────────────────────────────────
Write-Host "`n=== Helm history after rollback ===" -ForegroundColor Cyan
helm history microtask -n microtask

Write-Host "`n=== Pod status after rollback ===" -ForegroundColor Cyan
kubectl get pods -n microtask

Write-Host "`n=== Verifying all deployments are healthy ===" -ForegroundColor Cyan
kubectl rollout status deployment/api -n microtask --timeout=2m
kubectl rollout status deployment/worker -n microtask --timeout=2m
kubectl rollout status deployment/frontend -n microtask --timeout=2m

Write-Host "`n=== StatefulSet status ===" -ForegroundColor Cyan
kubectl rollout status statefulset/mysql -n microtask --timeout=2m

Write-Host "`nRollback demonstration complete." -ForegroundColor Green
