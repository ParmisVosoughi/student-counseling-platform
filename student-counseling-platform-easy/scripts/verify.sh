#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "[1/4] Python syntax"
python3 -m py_compile backend/config/*.py backend/accounts/*.py backend/accounts/management/commands/*.py backend/counseling/*.py backend/dashboard/*.py backend/accounts/migrations/*.py backend/counseling/migrations/*.py
if python3 -c "import django" >/dev/null 2>&1; then
  echo "[2/4] Django checks/tests"
  (cd backend && USE_SQLITE=True python manage.py check)
  (cd backend && USE_SQLITE=True python manage.py test)
else
  echo "[2/4] Django dependencies not installed; skipping runtime tests"
fi
if [ -d frontend/node_modules ]; then
  echo "[3/4] Frontend build"
  (cd frontend && npm run build)
else
  echo "[3/4] node_modules not installed; skipping frontend build"
fi
echo "[4/4] Forbidden placeholder scan"
if grep -RInE 'TODO|FIXME|MVP|Prototype|Sample Application' backend frontend/src --exclude-dir=node_modules; then
  echo "Forbidden placeholder/demo wording found"; exit 1
fi
echo "Verification complete"
