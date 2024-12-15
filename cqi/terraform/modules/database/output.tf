output "secret_arn" {
  value = aws_secretsmanager_secret.database.arn
}

output "database_arn" {
  value = aws_db_instance.default.arn
}
