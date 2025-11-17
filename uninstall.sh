#!/bin/bash

# StrmConvert Uninstallation Script for Linux
# This script removes StrmConvert and its systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INSTALL_DIR="/opt/strmconvert"
SERVICE_NAME="strmconvert"
SERVICE_USER="strmconvert"

echo -e "${YELLOW}StrmConvert Uninstallation Script${NC}"
echo "===================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Stop and disable service
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        echo "Stopping service..."
        systemctl stop "$SERVICE_NAME" || true
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        echo "Disabling service..."
        systemctl disable "$SERVICE_NAME" || true
    fi
else
    echo "Service not found, skipping stop/disable steps."
fi

# Remove systemd service file
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing systemd service file..."
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing installation directory: $INSTALL_DIR"
    read -p "Do you want to remove the installation directory and all its contents? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}Installation directory removed.${NC}"
    else
        echo -e "${YELLOW}Installation directory kept at: $INSTALL_DIR${NC}"
    fi
fi

# Optionally remove service user
if id "$SERVICE_USER" &>/dev/null; then
    read -p "Do you want to remove the service user '$SERVICE_USER'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        userdel "$SERVICE_USER" 2>/dev/null || true
        echo -e "${GREEN}Service user removed.${NC}"
    else
        echo -e "${YELLOW}Service user kept: $SERVICE_USER${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Uninstallation completed!${NC}"
echo ""

