# IAM role for data processing Lambda
resource "aws_iam_role" "data_processing_lambda_role" {
  name = "${var.project_name}-data-processing-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM role for recommendation Lambda  
resource "aws_iam_role" "recommendation_lambda_role" {
  name = "${var.project_name}-recommendation-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM role for authorizer Lambda
resource "aws_iam_role" "authorizer_lambda_role" {
  name = "${var.project_name}-authorizer-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  for_each = toset([
    aws_iam_role.data_processing_lambda_role.name,
    aws_iam_role.recommendation_lambda_role.name,
    aws_iam_role.authorizer_lambda_role.name
  ])

  role       = each.key
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# SQS access for data processing Lambda
resource "aws_iam_role_policy" "sqs_access_policy" {
  name = "${var.project_name}-sqs-access"
  role = aws_iam_role.data_processing_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.event_message_broker.arn
      }
    ]
  })
}