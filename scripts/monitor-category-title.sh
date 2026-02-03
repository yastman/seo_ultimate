#!/bin/bash
# Monitor workers for category-title update
declare -A WINDOW_MAP=(["w1-ru-clean"]="W1-RU" ["w2-uk-clean"]="W2-UK" ["w3-uk-skill"]="W3-SKILL")
LOGS_DIR="/home/user/projects/seo-ultimate/logs"

while true; do
  all_complete=true
  for k in "${!WINDOW_MAP[@]}"; do
    if grep -q '\[COMPLETE\]' "${LOGS_DIR}/${k}.log" 2>/dev/null; then
      echo "[$(date +%H:%M:%S)] ${k} COMPLETE"
      tmux kill-window -t "${WINDOW_MAP[$k]}" 2>/dev/null
    else
      all_complete=false
    fi
  done

  if $all_complete; then
    echo "[$(date +%H:%M:%S)] ALL WORKERS COMPLETE"
    exit 0
  fi

  sleep 30
done
