terraform {
  backend "s3" {
    bucket = "capstone-terraform-state-437229446821"
    key    = "global/ecr/terraform.tfstate" # Unique path!
    region = "ap-south-1"
    use_lockfile = true
  }
}
