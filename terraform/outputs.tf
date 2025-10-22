output "sqs_queue_url" {
  description = "SQS Queue URL for EventMessageBroker"
  value       = aws_sqs_queue.event_message_broker.url
}

output "data_processing_lambda_name" {
  description = "Data Processing Lambda function name"
  value       = aws_lambda_function.data_processing_lambda.function_name
}

output "recommendation_lambda_name" {
  description = "Recommendation Lambda function name"
  value       = aws_lambda_function.recommendation_lambda.function_name
}

output "authorizer_lambda_name" {
  description = "Authorizer Lambda function name"
  value       = aws_lambda_function.authorizer_lambda.function_name
}