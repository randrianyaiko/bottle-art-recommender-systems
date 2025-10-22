variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "recommender-system"
}

variable "lambda_layers_bucket" {
  description = "S3 bucket for lambda layers"
  type        = string
  default     = "lambda-layers-bucket-202510"
}

variable "authorizer_layer_version" {
  description = "Authorizer layer version"
  type        = string
  default     = "latest"
}

variable "common_layer_version" {
  description = "Common layer version"
  type        = string
  default     = "latest"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "default"
}

variable "qdrant_url" {
  description = "Qdrant database URL"
  type        = string
  sensitive   = true
}

variable "qdrant_api_key" {
  description = "Qdrant API key"
  type        = string
  sensitive   = true
}

variable "qdrant_collection_name" {
  description = "Qdrant collection name"
  type        = string
  default     = "users_interractions"
}

variable "qdrant_sparse_name" {
  description = "Qdrant sparse vector name"
  type        = string
  default     = "sparse"
}

variable "jwt_secret" {
  description = "JWT secret key for token validation"
  type        = string
  sensitive   = true
}
