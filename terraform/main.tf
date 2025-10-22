# Lambda Layers
resource "aws_lambda_layer_version" "authorizer_layer" {
  layer_name          = "${var.project_name}-authorizer-layer"
  description         = "PyJWT layer for authorizer Lambda"
  s3_bucket           = var.lambda_layers_bucket
  s3_key              = "layers/authorizer-layer-${var.authorizer_layer_version}.zip"
  compatible_runtimes = ["python3.10"]
}

resource "aws_lambda_layer_version" "common_layer" {
  layer_name          = "${var.project_name}-common-layer"
  description         = "Common dependencies for processing and recommendation Lambdas"
  s3_bucket           = var.lambda_layers_bucket
  s3_key              = "layers/common-layer-${var.common_layer_version}.zip"
  compatible_runtimes = ["python3.10"]
}

# SQS Dead Letter Queue
resource "aws_sqs_queue" "event_message_broker_dlq" {
  name                      = "EventMessageBrokerDLQ"
  message_retention_seconds = 1209600 # 14 days
}

# Main SQS Queue
resource "aws_sqs_queue" "event_message_broker" {
  name                      = "EventMessageBroker"
  message_retention_seconds = 86400   # 24 hours
  visibility_timeout_seconds = 30     # Matches Lambda timeout
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.event_message_broker_dlq.arn
    maxReceiveCount     = 3
  })
}

# Data Processing Lambda
resource "aws_lambda_function" "data_processing_lambda" {
  function_name = "${var.project_name}-data-processing"
  role          = aws_iam_role.data_processing_lambda_role.arn
  handler       = "lambda_handlers.event_processor.handler"
  runtime       = "python3.10"
  timeout       = 30
  memory_size   = 128
  s3_bucket     = var.lambda_code_bucket
  s3_key        = "lambda_code/code.zip"

  layers = [aws_lambda_layer_version.common_layer.arn]

  environment {
    variables = {
      QDRANT_URL    = var.qdrant_url
      QDRANT_API_KEY = var.qdrant_api_key
    }
  }
}

# Recommendation Lambda
resource "aws_lambda_function" "recommendation_lambda" {
  function_name = "${var.project_name}-recommendation"
  role          = aws_iam_role.recommendation_lambda_role.arn
  handler       = "lambda_handlers.recommender.handler"
  runtime       = "python3.10"
  timeout       = 30
  memory_size   = 128

  s3_bucket     = var.lambda_code_bucket
  s3_key        = "lambda_code/code.zip"

  layers = [aws_lambda_layer_version.common_layer.arn]

  environment {
    variables = {
      QDRANT_URL    = var.qdrant_url
      QDRANT_API_KEY = var.qdrant_api_key
    }
  }
}

# Authorizer Lambda
resource "aws_lambda_function" "authorizer_lambda" {
  function_name = "${var.project_name}-authorizer"
  role          = aws_iam_role.authorizer_lambda_role.arn
  handler       = "lambda_handlers.authorizer.handler"
  runtime       = "python3.10"
  timeout       = 30
  memory_size   = 128

  s3_bucket     = var.lambda_code_bucket
  s3_key        = "lambda_code/code.zip"

  layers = [aws_lambda_layer_version.authorizer_layer.arn]

  environment {
    variables = {
      JWT_SECRET = var.jwt_secret
    }
  }
}

# SQS Trigger for Data Processing Lambda
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.event_message_broker.arn
  function_name    = aws_lambda_function.data_processing_lambda.arn
  batch_size       = 10  # As requested
}

# API Gateway
resource "aws_apigatewayv2_api" "main_api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

# API Gateway Authorizer
resource "aws_apigatewayv2_authorizer" "jwt_authorizer" {
  api_id           = aws_apigatewayv2_api.main_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = aws_lambda_function.authorizer_lambda.invoke_arn
  identity_sources = ["$request.header.Authorization"]
  name             = "jwt-authorizer"
  authorizer_payload_format_version = "2.0"
}

# API Gateway Integration for Recommendation Lambda
resource "aws_apigatewayv2_integration" "recommendation_integration" {
  api_id             = aws_apigatewayv2_api.main_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.recommendation_lambda.invoke_arn
  integration_method = "POST"
}

# API Gateway Route
resource "aws_apigatewayv2_route" "recommendation_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "GET /recommendation"
  target    = "integrations/${aws_apigatewayv2_integration.recommendation_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type = "CUSTOM"
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id = aws_apigatewayv2_api.main_api.id
  name   = "$default"
  auto_deploy = true
}

# Lambda Permissions for API Gateway
resource "aws_lambda_permission" "api_gateway_authorizer" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_recommendation" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.recommendation_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main_api.execution_arn}/*/*"
}