#!/bin/bash

# StrmConvert Installation Script for Linux
# This script installs StrmConvert as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="/opt/strmconvert"
SERVICE_NAME="strmconvert"
SERVICE_USER="strmconvert"

echo -e "${GREEN}StrmConvert Installation Script${NC}"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check Python version (need 3.7+)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    echo -e "${RED}Python 3.7 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
# Exclude install/uninstall scripts from installation directory
rm -f "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh"

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd -r -s /bin/false "$SERVICE_USER"
else
    echo "Service user already exists: $SERVICE_USER"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$INSTALL_DIR"
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt --quiet

# Set ownership
echo "Setting file ownership..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Create systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=StrmConvert - .strm file path converter and monitor
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start service automatically
echo "Enabling service..."
systemctl enable "$SERVICE_NAME"

echo "Starting service..."
systemctl start "$SERVICE_NAME"

# Wait a moment for service to start
sleep 2

# Check if service started successfully
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}Service started successfully!${NC}"
else
    echo -e "${YELLOW}Warning: Service may not have started properly.${NC}"
    echo "Please check the status with: sudo systemctl status $SERVICE_NAME"
fi

echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo "The service has been enabled and started automatically."
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status $SERVICE_NAME"
echo "  - View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Stop service: sudo systemctl stop $SERVICE_NAME"
echo "  - Restart service: sudo systemctl restart $SERVICE_NAME"
echo ""
echo "Configuration file: $INSTALL_DIR/config.yaml"
echo "The web UI will be available at: http://localhost:9115"
echo ""

