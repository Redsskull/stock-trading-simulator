#!/bin/bash
flask db upgrade
exec gunicorn app:app --log-level=debug --access-logfile - --error-logfile -
