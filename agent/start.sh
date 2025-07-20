#!/bin/bash
set -e

# Pre-create /tmp/.X11-unix as root if possible (harmless if already exists)
if [ "$(id -u)" = "0" ]; then
  mkdir -p /tmp/.X11-unix
  chmod 1777 /tmp/.X11-unix
fi

export DISPLAY=:1
Xvfb :1 -screen 0 1280x800x16 &
fluxbox &
vncserver :1 -geometry 1280x800 -depth 16 &

# Start websockify for NoVNC (use PATH)
if command -v websockify >/dev/null 2>&1; then
  websockify 8080 localhost:5901 &
else
  echo "websockify not found in PATH! NoVNC will not work."
fi

jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root &
# Run Flask agent server on port 5000 to avoid conflict with NoVNC
python3 /home/agent/agent_server.py --port 5000 