#!/usr/bin/env bash
# Run the executable contracts end to end.
#
#   ./verify.sh
#
# Starts the app on a scratch database and an unused port, runs every contract
# in cmdb/knowledge/contracts through contracts/run.mjs, then stops the app and
# deletes the scratch database. Nothing touches cmdb.db or any real deployment.
#
# A scratch database matters: two scenarios state a precondition ("an empty
# CMDB", "discovery_history has no rows") that cannot be manufactured through
# the API, and their Given checks it rather than assuming it. Against a used
# database they fail honestly instead of passing quietly.
#
# Environment:
#   PYTHON          python to use (default: .venv/bin/python, else python3)
#   CONTRACT_PORT   port to bind (default: 5967)

set -euo pipefail
cd "$(dirname "$0")"

PORT="${CONTRACT_PORT:-5967}"
BASE="http://127.0.0.1:${PORT}"

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi

WORKDIR="$(mktemp -d)"
DB="${WORKDIR}/contracts.db"
LOG="${WORKDIR}/app.log"
APP_PID=""

cleanup() {
  if [ -n "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null; then
    kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
  fi
  rm -rf "$WORKDIR"
}
trap cleanup EXIT INT TERM

echo "Starting cmdb on ${BASE} against a scratch database"
# Started by import, exactly as a WSGI server would (see ISS-107).
CMDB_DB="$DB" "$PYTHON" -c "import app; app.app.run(port=${PORT})" >"$LOG" 2>&1 &
APP_PID=$!

for _ in $(seq 1 60); do
  if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo "The app exited before it began serving:"
    tail -n 40 "$LOG"
    exit 2
  fi
  if curl -fsS -o /dev/null "${BASE}/api/stats" 2>/dev/null; then break; fi
  sleep 0.25
done

if ! curl -fsS -o /dev/null "${BASE}/api/stats" 2>/dev/null; then
  echo "The app never answered on ${BASE}:"
  tail -n 40 "$LOG"
  exit 2
fi

set +e
node contracts/run.mjs --base "$BASE" "$@"
STATUS=$?
set -e

if [ "$STATUS" -ne 0 ]; then
  echo
  echo "--- app log ---"
  tail -n 40 "$LOG"
fi

exit "$STATUS"
