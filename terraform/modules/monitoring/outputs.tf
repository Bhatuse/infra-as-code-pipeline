output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}

output "cpu_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.cpu_high.arn
}
