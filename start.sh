#!/bin/bash

# Start the backend
cd lenze-backend
uvicorn main:app --reload &

# Start the frontend
cd ../lenze-frontend
npm start

# Wait for all processes to finish
wait
