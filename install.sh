#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define paths
MODEL_SCRIPT="${SCRIPT_DIR}/model/download_model.sh"
PYTHON_SCRIPT="${SCRIPT_DIR}/src/aicam.py"
LOG_FILE="${SCRIPT_DIR}/cron.log"

# Execute the download_model.sh script using bash
if [ -f "$MODEL_SCRIPT" ]; then
  bash "$MODEL_SCRIPT"
else
  echo "Error: $MODEL_SCRIPT not found."
  exit 1
fi

# Add a crontab entry to run the Python script at reboot
# Check if the crontab entry already exists
(crontab -l | grep -F "$PYTHON_SCRIPT") || (
  # Escape special characters in paths
  ESCAPED_PYTHON_SCRIPT=$(printf '%q' "$PYTHON_SCRIPT")
  ESCAPED_LOG_FILE=$(printf '%q' "$LOG_FILE")

  # Add the crontab entry
  (crontab -l; echo "@reboot /usr/bin/python3 $ESCAPED_PYTHON_SCRIPT >> $ESCAPED_LOG_FILE 2>&1") | crontab -
)

echo "Setup complete. The Python script will run at reboot, and output will be logged to $LOG_FILE."
