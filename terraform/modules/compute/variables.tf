variable "environment" {}
variable "ecr_repo_url" {}
variable "execution_role_arn" {}
variable "ecs_sg_id" {}
variable "target_group_arn" {}
variable "private_subnet_ids" { type = list(string) }
