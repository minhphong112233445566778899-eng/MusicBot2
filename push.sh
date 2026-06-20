#!/bin/bash

# Discord Music Bot - Quick Push Script
# This script helps you push the code to GitHub

echo "======================================"
echo "Discord Music Bot - GitHub Push"
echo "======================================"
echo ""
echo "Repository: https://github.com/minhphong112233445566778899-eng/MusicBot2.git"
echo ""
echo "Choose authentication method:"
echo "1. Personal Access Token"
echo "2. SSH Key"
echo "3. Show manual commands"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    read -p "Enter your GitHub Personal Access Token: " token
    cd /app
    git push https://${token}@github.com/minhphong112233445566778899-eng/MusicBot2.git main --force
    ;;
  2)
    cd /app
    git remote set-url origin git@github.com:minhphong112233445566778899-eng/MusicBot2.git
    git push -u origin main --force
    ;;
  3)
    echo ""
    echo "Manual Push Commands:"
    echo "---------------------"
    echo "cd /app"
    echo "git push -u origin main --force"
    echo ""
    echo "If authentication fails, use:"
    echo "git push https://<YOUR_TOKEN>@github.com/minhphong112233445566778899-eng/MusicBot2.git main --force"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
