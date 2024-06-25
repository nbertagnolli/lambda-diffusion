# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.10

# Install any dependencies
RUN pip install --no-cache-dir diffusers torch transformers

# Copy the model for the lambda
COPY segmind ${LAMBDA_TASK_ROOT}/segmind

# Copy the function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Command to run the Lambda function
CMD ["main.handler"]