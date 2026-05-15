terraform {
  backend "s3" {
    bucket       = "capstone-terraform-state-437229446821"
    key          = "dev/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
    encrypt      = true
  }
}

data "terraform_remote_state" "global_ecr" {
  backend = "s3"
  config = {
    bucket = "capstone-terraform-state-437229446821"
    key    = "global/ecr/terraform.tfstate"
    region = "ap-south-1"
  }
}
