# Stage 1: Builder
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage cache
COPY requirements.txt .

# Install dependencies into /install (isolated directory)
RUN pip install --no-cache-dir -r requirements.txt -t /install

# Now copy the application code
COPY lambda_function.py .
COPY src/ ./src
COPY lambda_handlers/ ${LAMBDA_TASK_ROOT}/lambda_handlers

# Stage 2: Lambda base image
FROM public.ecr.aws/lambda/python:3.10

# Copy installed packages from builder
COPY --from=builder /install ${LAMBDA_TASK_ROOT}/

# Copy application code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/src
COPY lambda_handlers/ ${LAMBDA_TASK_ROOT}/lambda_handlers
