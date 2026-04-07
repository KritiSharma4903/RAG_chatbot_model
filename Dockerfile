# Base Image
FROM python:3.12.4

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .
+

# Expose port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "Frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]





