module "teams" {
  source = "./modules/team"

  for_each  = toset(var.team_names)
  team_name = each.value
}

data "aws_secretsmanager_random_password" "internal_key" {
  password_length     = 20
  include_space       = false
}

resource "aws_secretsmanager_secret" "internal_key" {
  name                           = "internal_key"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "internal_key" {
  secret_id     = aws_secretsmanager_secret.internal_key.id
  secret_string = data.aws_secretsmanager_random_password.internal_key.random_password
}

resource "aws_security_group" "game_server_sg" {
  name_prefix = "game_server_sg_"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "game_server" {
  ami                         = "ami-0325498274077fac5" # Ubuntu 24.04 ARM64
  instance_type               = "t4g.nano"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.game_server_sg.id]

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  tags = {
    Name = "game_server"
  }
}

resource "namecheap_domain_records" "game_server_record" {
  domain = "cqiprog.info"
  mode   = "OVERWRITE"

  record {
    hostname = "@"
    type     = "A"
    address  = aws_instance.game_server.public_ip
    ttl      = 300 # 5 minutes
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2_ecr_role"

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

resource "aws_iam_policy" "ecr_policy" {
  name = "ecr_list_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_role_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ecr_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2_instance_profile"
  role = aws_iam_role.ec2_role.name
}
