terraform {
  backend "s3" {
    bucket       = "capstone-terraform-state-437229446821"
    key          = "production/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
    encrypt      = true
  }
}
