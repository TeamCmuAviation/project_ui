# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose port (Internal container port)
EXPOSE 8000

# Run gunicorn
# Adjust 'human_eval_project.wsgi:application' if your project name is different
CMD ["gunicorn", "human_eval_project.wsgi:application", "--bind", "0.0.0.0:8000"]
