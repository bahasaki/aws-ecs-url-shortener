variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "url-shortener"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "container_image" {
  description = "Docker image URI from ECR"
  type        = string
}