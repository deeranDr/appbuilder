#!/bin/bash

NEW_APP="$1"

if [ ! -f "$NEW_APP" ]; then
  echo "❌ Installer not found: $NEW_APP"
  exit 1
fi

echo "▶️ Launching updated installer..."
open "$NEW_APP"
sleep 2
exit 0
