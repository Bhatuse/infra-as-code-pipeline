resource "aws_ecr_repository" "app" {
  name                 = "pravin-capstone-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "capstone-ecr"
    Environment = "global"
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
