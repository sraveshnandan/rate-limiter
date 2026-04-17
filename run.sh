#!/bin/bash
echo "Starting Rate Limiter Test Environment..."

# Kill any existing processes on port 8000 and 5173 to avoid conflicts
lsof -t -i:8000 | xargs -r kill -9
lsof -t -i:5173 | xargs -r kill -9

# Start the Python FastAPI Backend in the background
echo "Starting FastAPI Backend on port 8000..."
cd test_backend
source venv/bin/activate
uvicorn main:app --port 8000 &
BACKEND_PID=$!
cd ..

# Start the React Vite Frontend in the background
echo "Starting React Frontend on port 5173..."
cd test_frontend
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo "--------------------------------------------------------"
echo "✅ Both servers are running!"
echo "🌐 React App: http://localhost:5173"
echo "⚙️  API Backend: http://localhost:8000"
echo "Press Ctrl+C to stop both servers."
echo "--------------------------------------------------------"

# Wait for Ctrl+C, then kill the background processes
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
