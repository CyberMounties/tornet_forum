#!/bin/bash
# entrypoint.sh

set -e  # Exit on error

echo "Starting entrypoint script..."

# Create database by running app.py briefly
echo "Creating database..."
python app.py &
APP_PID=$!
sleep 5  # Give app.py time to create database
kill $APP_PID 2>/dev/null || true  # Stop app.py

# Wait for database file to exist
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if [ -f instance/database.db ]; then
        echo "Database found!"
        break
    fi
    sleep 1
done

if [ ! -f instance/database.db ]; then
    echo "Error: Database not created after 30 seconds"
    exit 1
fi

# Populate database
echo "Populating database..."
python populate_db.py

# Start simulators in background
echo "Starting simulators..."
python sellers_simulator.py &
python shoutbox_simulator.py &

# Start gunicorn on port 5000
echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 app:app