# --- 1. The Cluster (The Folder) ---
resource "aws_ecs_cluster" "main" {
  name = "capstone-cluster-${var.environment}"
}

# --- 2. The Log Group (The Recorder) ---
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/my-app-${var.environment}"
  retention_in_days = 7
}

# --- 3. The Task Definition (The Blueprint) ---
resource "aws_ecs_task_definition" "app" {
  family                   = "my-app-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([{
    name      = "app"
    image     = "${var.ecr_repo_url}:latest"
    portMappings = [{ containerPort = 3000 }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/my-app-${var.environment}"
        awslogs-region        = "ap-south-1"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

# --- 4. The Service (The Manager) ---
resource "aws_ecs_service" "app" {
  name            = "app-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "app"
    container_port   = 3000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true # This is the magic "Undo" button
  }

  deployment_controller {
    type = "ECS"
  }

  health_check_grace_period_seconds = 60
  
}
