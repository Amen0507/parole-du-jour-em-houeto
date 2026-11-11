#!/bin/bash
# Exécution quotidienne à placer dans crontab (ex: 0 5 * * * /chemin/vers/scripts/cron_daily.sh)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

# Activer environnement ou lancer directement
python3 scripts/generate_daily.py >> output/daily.log 2>&1
