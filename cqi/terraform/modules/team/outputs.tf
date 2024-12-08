output "ecr_name" {
  description = "The name of the ECR repository"
  value       = aws_ecr_repository.team_repo.name
}

output "ecr_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.team_repo.repository_url
}

output "access_key" {
  description = "The access key for the team"
  value       = aws_iam_access_key.team_user_access_key.id
}

output "secret_key" {
  description = "The secret key for the team"
  value       = aws_iam_access_key.team_user_access_key.secret
}
