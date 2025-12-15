#!/bin/bash
# ==========================================
# 🚀 Premedia App Updater (macOS)
# ==========================================

# $1 = new DMG or PKG path
NEW_APP="$1"

echo "▶️ Launching updated installer..."
open "$NEW_APP"
echo "✅ Update complete. Enjoy the new version!"
sleep 2
exit 0