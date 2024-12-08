resource "aws_ecr_repository" "team_repo" {
  name = lower(var.team_name)
  force_delete = true
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
