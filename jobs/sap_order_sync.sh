#!/bin/bash

LOCKFILE="/app/despachos/jobs/sap_order_sync.lock"
PYTHON_SCRIPT="/app/despachos/jobs/sap_order_sync.py"
MANAGE_PY="/app/despachos/manage.py"
VENV_PYTHON="/app/despachos/venv/bin/python3"

(
    flock -n 9 || exit 1
    # Setup a trap to ensure the lock is released
    trap 'rm -f "$LOCKFILE"' EXIT

    # Run the Python script
    $VENV_PYTHON $MANAGE_PY shell < $PYTHON_SCRIPT

) 9>"$LOCKFILE"
