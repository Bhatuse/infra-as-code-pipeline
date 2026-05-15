output "alb_sg_id" {
  value = aws_security_group.alb_sg.id
}

output "ecs_sg_id" {
  value = aws_security_group.ecs_sg.id
}

output "execution_role_arn" {
  value = aws_iam_role.ecs_task_execution_role.arn
}
