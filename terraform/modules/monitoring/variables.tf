variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster to monitor"
  type        = string
}

variable "service_name" {
  description = "Name of the ECS service to monitor"
  type        = string
}
