module "instance" {
  source = "./instance"

  count           = var.instance_count
  instance_number = count.index

  ssh_key_name          = var.ssh_key_name
  global_secrets        = var.global_secrets
  domain                = var.domain
  instance_profile_name = aws_iam_instance_profile.ec2_instance_profile.name
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2_runner_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ec2_policy" {
  name = "runner_list_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          var.internal_key_arn,
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_role_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2_runner_instance_profile"
  role = aws_iam_role.ec2_role.name
}
