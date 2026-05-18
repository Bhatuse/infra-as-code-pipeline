# CloudWatch Dashboard
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "ECS-Monitoring-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "app-service-${var.environment}", "ClusterName", "capstone-cluster-${var.environment}"]
          ]
          period = 300
          stat   = "Average"
          region = "ap-south-1"
          title  = "App CPU Usage"
        }
      }
    ]
  })
}

# Alarm: If CPU is too high
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ecs cpu utilization"
}
