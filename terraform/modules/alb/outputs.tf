output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}

output "alb_dns_name" {
  description = "The URL you will use to access your app"
  value       = aws_lb.main.dns_name
}
