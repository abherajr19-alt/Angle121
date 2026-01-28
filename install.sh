#!/data/data/com.termux/files/usr/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 नोवा असिस्टेंट इंस्टॉलेशन शुरू...${NC}"

# Update packages
echo -e "${YELLOW}📦 पैकेजेस अपडेट हो रही हैं...${NC}"
pkg update -y && pkg upgrade -y

# Install required packages
echo -e "${YELLOW}📦 जरूरी पैकेजेस इंस्टॉल हो रही हैं...${NC}"
pkg install -y python git wget curl termux-api android-tools

# Install Python packages
echo -e "${YELLOW}🐍 पायथन पैकेजेस इंस्टॉल हो रही हैं...${NC}"
pip install --upgrade pip
pip install requests flask colorama

# Install speech recognition if needed
# pip install SpeechRecognition pydub

# Create Nova directory
echo -e "${YELLOW}📁 नोवा डायरेक्टरी बन रही है...${NC}"
mkdir -p ~/.nova
mkdir -p ~/.nova/backups
mkdir -p ~/.nova/logs

# Copy files
echo -e "${YELLOW}📄 फाइल्स कॉपी हो रही हैं...${NC}"
cp *.py ~/.nova/
cp *.json ~/.nova/ 2>/dev/null || true
cp *.sh ~/.nova/

# Make scripts executable
chmod +x ~/.nova/*.py
chmod +x ~/.nova/*.sh

# Setup ADB
echo -e "${YELLOW}🔌 ADB सेटअप हो रहा है...${NC}"
adb kill-server
adb start-server

echo -e "${GREEN}✅ ADB सर्वर शुरू हो गया${NC}"
echo -e "${YELLOW}📱 अब अपने फोन में जाएं:${NC}"
echo -e "1. Settings > About Phone > Tap Build Number 7 times"
echo -e "2. Developer Options में जाएं"
echo -e "3. USB Debugging और Wireless Debugging चालू करें"
echo -e "4. इस कमांड को रन करें: ${GREEN}adb tcpip 5555${NC}"
echo -e "5. फिर: ${GREEN}adb connect localhost:5555${NC}"

# Create startup script
echo -e "${YELLOW}🚀 स्टार्टअप स्क्रिप्ट बन रही है...${NC}"
cat > ~/.nova/start_nova.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

cd ~/.nova

echo "🌟 नोवा शुरू हो रही है..."

# Check ADB connection
adb_state=$(adb get-state 2>&1)
if [[ "$adb_state" != "device" ]]; then
    echo "🔌 ADB कनेक्ट कर रहा हूं..."
    adb connect localhost:5555
    
    # Check again
    adb_state=$(adb get-state 2>&1)
    if [[ "$adb_state" != "device" ]]; then
        echo "⚠️ ADB कनेक्ट नहीं हो पाया"
        echo "कृपया मैन्युअली कनेक्ट करें: adb connect localhost:5555"
    fi
fi

# Start Nova
python main.py
EOF

chmod +x ~/.nova/start_nova.sh

# Create alias
echo -e "${YELLOW}🔗 एलियास बन रहा है...${NC}"
echo "alias nova='cd ~/.nova && python main.py'" >> ~/.bashrc
echo "alias start-nova='bash ~/.nova/start_nova.sh'" >> ~/.bashrc

# Create auto-start service
echo -e "${YELLOW}🔄 ऑटो-स्टार्ट सर्विस सेटअप...${NC}"
cat > ~/.nova/nova_service.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

while true; do
    cd ~/.nova
    python main.py
    echo "Nova crashed, restarting in 5 seconds..."
    sleep 5
done
EOF

chmod +x ~/.nova/nova_service.sh

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ इंस्टॉलेशन पूर्ण!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}नोवा को स्टार्ट करने के लिए:${NC}"
echo -e "1. ${GREEN}start-nova${NC} - Normal start"
echo -e "2. ${GREEN}nova${NC} - Direct start"
echo -e "3. ${GREEN}bash ~/.nova/nova_service.sh${NC} - Auto-restart service"
echo -e ""
echo -e "${YELLOW}पहली बार सेटअप:${NC}"
echo -e "1. अपने फोन में Developer Options चालू करें"
echo -e "2. USB Debugging चालू करें"
echo -e "3. टर्मिनल में चलाएं: ${GREEN}adb connect localhost:5555${NC}"
echo -e "${GREEN}========================================${NC}"

# Reload bashrc
source ~/.bashrc
