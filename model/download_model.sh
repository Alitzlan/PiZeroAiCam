#!/bin/bash

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TEST_DATA_URL="https://github.com/google-coral/test_data/raw/master/"
readonly TEST_DATA_DIR="${SCRIPT_DIR}/mobilenet_coco"

# List of files to download
files=(
  "ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
  "coco_labels.txt"
)

# Create the target directory
mkdir -p "${TEST_DATA_DIR}"

# Iterate over each file
for file in "${files[@]}"; do
  # Verify the file exists on the server
  response="$(curl -Lso /dev/null -w "%{http_code}" "${TEST_DATA_URL}/${file}")"
  if [[ "${response}" == "200" ]]; then
    echo "DOWNLOAD: ${file}"
    # Handle subdirectories in the file path
    if [[ "${file}" == */* ]]; then
      subdir="$(dirname "${file}")"
      mkdir -p "${TEST_DATA_DIR}/${subdir}"
      (cd "${TEST_DATA_DIR}/${subdir}" && curl -OL "${TEST_DATA_URL}/${file}")
    else
      (cd "${TEST_DATA_DIR}" && curl -OL "${TEST_DATA_URL}/${file}")
    fi
  else
    echo "NOT FOUND: ${file}"
  fi
done
