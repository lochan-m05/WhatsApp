#!/bin/bash

echo "🚀 Setting up WhatsApp Bulk Messaging System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Chrome (if not already installed)
if ! command -v google-chrome &> /dev/null; then
    echo "🌐 Installing Google Chrome..."
    
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
        
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS/Fedora
        sudo yum install -y google-chrome-stable
        
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S google-chrome
        
    else
        echo "⚠️  Please install Google Chrome manually"
    fi
else
    echo "✅ Google Chrome is already installed"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs config

# Set permissions
chmod +x main.py
chmod +x setup.sh

# Create desktop shortcut (optional)
if command -v xdg-desktop-menu &> /dev/null; then
    echo "🖥️  Creating desktop shortcut..."
    
    cat > whatsapp-placement.desktop << EOF
[Desktop Entry]
Name=WhatsApp Placement System
Comment=Bulk messaging system for placement offers
Exec=$(pwd)/venv/bin/python $(pwd)/main.py
Icon=applications-internet
Terminal=true
Type=Application
Categories=Network;
EOF
    
    xdg-desktop-menu install whatsapp-placement.desktop
fi

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Quick Start Guide:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. View help: python main.py --help"
echo "3. Send messages: python main.py send --company 'TechCorp' --position 'Developer' --package '10 LPA' --location 'Mumbai' --deadline '2024-02-01'"
echo "4. Start scheduler: python main.py scheduler start"
echo "5. Check status: python main.py status"
echo ""
echo "📝 Note: Make sure to scan WhatsApp QR code on first use!"
