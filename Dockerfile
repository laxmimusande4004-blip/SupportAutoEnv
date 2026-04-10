# Use official Python image
FROM python:3.10-slim

# Set environment variables for better performance
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create non-root user (required by HuggingFace Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install Python requirements
RUN pip install --no-cache-dir --user \
    fastapi \
    uvicorn[standard] \
    pydantic \
    huggingface_hub \
    websockets

# Copy project files
COPY --chown=user . .

# HuggingFace Spaces uses port 7860
EXPOSE 7860

# Run the FastAPI server on port 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
