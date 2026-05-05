#!/bin/bash
# Monitor plural validation workers

declare -A WINDOW_MAP=(
    ["worker-code"]="W-CODE"
    ["worker-skills"]="W-SKILLS"
)

LOG_DIR="/home/user/projects/llm-keywords-pipeline/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitor started"

while true; do
    all_complete=true

    for k in "${!WINDOW_MAP[@]}"; do
        log_file="${LOG_DIR}/${k}.log"
        window="${WINDOW_MAP[$k]}"

        if grep -q '\[COMPLETE\]' "$log_file" 2>/dev/null; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] $k COMPLETE - closing $window"
            tmux kill-window -t "$window" 2>/dev/null
        else
            all_complete=false
        fi
    done

    if $all_complete; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] All workers complete!"
        break
    fi

    sleep 30
done
