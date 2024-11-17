output "ecr_name" {
  description = "The name of the ECR repository"
  value       = aws_ecr_repository.team_repo.name
}

output "ecr_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.team_repo.repository_url
}
