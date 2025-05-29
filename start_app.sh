echo "Checking for processes on port 5000..."
PID=$(lsof -i :5000 -t)
if [ -n "$PID" ]; then
    echo "Port 5000 is in use by PID $PID. Killing the process..."
    kill -9 $PID
    sleep 1
fi
echo "Starting Flask app..."
python app.py