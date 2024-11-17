resource "aws_ecr_repository" "team_repo" {
  name = lower(var.team_name)
}

resource "aws_iam_user" "team_user" {
  name          = "${var.team_name}_user"
  force_destroy = true
}

resource "aws_iam_user_policy" "team_user_policy" {
  name = "${var.team_name}_policy"
  user = aws_iam_user.team_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Effect   = "Allow"
        Resource = aws_ecr_repository.team_repo.arn
      }
    ]
  })
}

resource "aws_iam_access_key" "team_user_access_key" {
  user = aws_iam_user.team_user.name
}

resource "aws_secretsmanager_secret" "user_secret" {
  name                           = "${lower(var.team_name)}_secret"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "user_secret" {
  secret_id     = aws_secretsmanager_secret.user_secret.id
  secret_string = jsonencode({ id : aws_iam_access_key.team_user_access_key.id, key : aws_iam_access_key.team_user_access_key.secret })
}
