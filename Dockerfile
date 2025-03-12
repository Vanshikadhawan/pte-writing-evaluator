# Stage 1: Run DeepSeek (Ollama)
FROM ubuntu:22.04 as deepseek

WORKDIR /app
RUN apt-get update && apt-get install -y wget curl

# Install Ollama (DeepSeek)
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama pull deepseek-r1:7b

# Expose DeepSeek port
EXPOSE 11434
CMD ["ollama", "serve"]


# Stage 2: Run Flask App
FROM python:3.10

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose Flask app port
EXPOSE 5000
CMD ["python", "app.py"]
