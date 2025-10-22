provider "aws" {
  region = "us-east-1"  # Change as needed
}

############################
# 1. SQS Queue
############################
resource "aws_sqs_queue" "my_queue" {
  name                      = "my-sqs-queue"
  visibility_timeout_seconds = 30
}

############################
# 2. IAM Role for Lambda
############################
resource "aws_iam_role" "lambda_role" {
  name = "lambda_sqs_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

############################
# 3. IAM Policies
############################
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

############################
# 4. Lambda Function (Python)
############################
resource "aws_lambda_function" "my_lambda" {
  function_name = "sqs_trigger_lambda"
  handler       = "lambda_function.lambda_handler" # Python file and function
  runtime       = "python3.11"                       # Use latest supported runtime

  role = aws_iam_role.lambda_role.arn

  filename         = "lambda.zip"                   # Your zipped Python code
  source_code_hash = filebase64sha256("lambda.zip")
}

############################
# 5. Event Source Mapping
############################
resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn = aws_sqs_queue.my_queue.arn
  function_name    = aws_lambda_function.my_lambda.arn
  batch_size       = 10
  enabled          = true
}
