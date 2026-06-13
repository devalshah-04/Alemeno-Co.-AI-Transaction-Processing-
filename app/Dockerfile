# Start from a lightweight official Python image
FROM python:3.12-slim

# All following commands run from this folder inside the container
WORKDIR /code

# Copy just the requirements file first
COPY requirements.txt .

# Install the Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code into the container
COPY . .

# Command that runs when the container starts:
# start uvicorn, serving the "app" object from main.py, reachable from any IP, on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]