module "networking" {
  source      = "../../modules/networking"
  environment = "dev"
  vpc_cidr    = "10.1.0.0/16"
}

module "security" {
  source      = "../../modules/security"
  environment = "dev"
  vpc_id      = module.networking.vpc_id
}

module "alb" {
  source            = "../../modules/alb"
  environment       = "dev"
  vpc_id            = module.networking.vpc_id
  public_subnet_ids = module.networking.public_subnet_ids
  alb_sg_id         = module.security.alb_sg_id
}

module "compute" {
  source             = "../../modules/compute"
  environment        = "dev"
  ecr_repo_url       = data.terraform_remote_state.global_ecr.outputs.ecr_repository_url
  execution_role_arn = module.security.execution_role_arn
  ecs_sg_id          = module.security.ecs_sg_id
  private_subnet_ids = module.networking.private_subnet_ids
  target_group_arn   = module.alb.target_group_arn
}

module "monitoring" {
  source       = "../../modules/monitoring"
  environment  = "dev"
  cluster_name = module.compute.cluster_name
  service_name = "app-service-dev" # This matches the name defined in modules/compute/main.tf
}
