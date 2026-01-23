#!/bin/bash

# 🧹 NanoToolz Repository Cleanup Script
# This script removes all unnecessary files and folders

echo "🧹 Starting NanoToolz Repository Cleanup..."
echo "⚠️  This will delete unnecessary files permanently!"
echo ""

# Function to safely remove files/folders
safe_remove() {
    if [ -e "$1" ]; then
        echo "🗑️  Removing: $1"
        rm -rf "$1"
    else
        echo "⚪ Not found: $1"
    fi
}

echo "📂 Removing duplicate/empty bot structure..."
safe_remove "bot/"

echo "📄 Removing excessive documentation..."
safe_remove "00_START_HERE.md"
safe_remove "SETUP.md" 
safe_remove "DEPLOYMENT.md"
safe_remove "FEATURES.py"
safe_remove "QUICKSTART.py"
safe_remove "START_HERE.py"
safe_remove "COMPLETION_REPORT.txt"

echo "🌐 Removing empty web folders..."
safe_remove "web/static/"
safe_remove "web/templates/"

echo "🔧 Removing validation scripts..."
safe_remove "validate_setup.py"
safe_remove "setup.sh"

echo "🧹 Removing cleanup files..."
safe_remove "CLEANUP_PLAN.md"

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📊 Remaining structure:"
echo "├── main.py"
echo "├── requirements.txt"
echo "├── .env"
echo "├── README.md"
echo "├── LICENSE"
echo "├── src/"
echo "│   ├── bot/handlers.py"
echo "│   ├── database/"
echo "│   ├── config.py"
echo "│   ├── seed.py"
echo "│   └── utils.py"
echo "└── web/admin.py"
echo ""
echo "🚀 Your repository is now clean and professional!"