module "teams" {
  source = "./modules/team"

  for_each  = toset(var.team_names)
  team_name = each.value
}

module "database" {
  source = "./modules/database"
  ec2_security_group_id = aws_security_group.main_server_sg.id
}

resource "aws_secretsmanager_secret" "user_secrets" {
  name                           = "user_secrets"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "user_secret" {
  secret_id = aws_secretsmanager_secret.user_secrets.id
  secret_string = jsonencode({ for team, mod in module.teams : team => {
    access = mod.access_key
    secret = mod.secret_key
  } })
}

data "aws_secretsmanager_random_password" "internal_key" {
  password_length     = 30
  include_space       = false
  exclude_punctuation = true
}

resource "aws_secretsmanager_secret" "internal_key" {
  name                           = "internal_key"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "internal_key" {
  secret_id     = aws_secretsmanager_secret.internal_key.id
  secret_string = data.aws_secretsmanager_random_password.internal_key.random_password

  lifecycle {
    ignore_changes = [secret_string, ]
  }
}

resource "aws_security_group" "main_server_sg" {
  name_prefix = "main_server_sg_"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
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

resource "aws_security_group" "game_runner_sg" {
  name_prefix = "game_runner_sg_"

  ingress {
    from_port   = 22
    to_port     = 22
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

resource "aws_instance" "main_server" {
  ami                         = "ami-0325498274077fac5" # Ubuntu 24.04 ARM64
  instance_type               = "t4g.nano"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.main_server_sg.id]
  key_name                    = aws_key_pair.default_ssh_key.key_name

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = base64decode(nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).ssh_private_key))
    host        = self.public_ip
    timeout     = "6m"
  }

  provisioner "file" {
    source      = "./scripts/main_server"
    destination = "./"
  }

  provisioner "remote-exec" {
    inline = [
      "cd /home/ubuntu/main_server",
      "chmod +x ./init.sh",
      "curl -s 'https://dynamicdns.park-your-domain.com/update?host=${var.domain.main_server}&domain=${var.domain.address}&password=${nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).namecheap_key)}&ip=${self.public_ip}'",
      "sudo GITHUB_TOKEN='${nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).github_token)}' ./init.sh",
    ]
  }

  tags = {
    Name = "main_server"
  }

  depends_on = [ module.database ]
}

resource "aws_instance" "game_runner" {
  ami                         = "ami-0325498274077fac5" # Ubuntu 24.04 ARM64
  instance_type               = "t4g.nano"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.game_runner_sg.id]
  key_name                    = aws_key_pair.default_ssh_key.key_name

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = base64decode(nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).ssh_private_key))
    host        = self.public_ip
    timeout     = "6m"
  }

  provisioner "file" {
    source      = "./scripts/game_runner"
    destination = "./"
  }

  provisioner "remote-exec" {
    inline = [
      "cd /home/ubuntu/game_runner",
      "chmod +x ./init.sh",
      "curl -s 'https://dynamicdns.park-your-domain.com/update?host=${var.domain.game_runner}&domain=${var.domain.address}&password=${nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).namecheap_key)}&ip=${self.public_ip}'",
      "sudo GITHUB_TOKEN='${nonsensitive(jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).github_token)}' ./init.sh",
    ]
  }

  tags = {
    Name = "game_runner"
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2_role"

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
  name = "ecr_list_policy"

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
          aws_secretsmanager_secret.internal_key.arn,
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
  name = "ec2_instance_profile"
  role = aws_iam_role.ec2_role.name
}

data "aws_secretsmanager_secret" "global_secrets" {
  arn = "arn:aws:secretsmanager:us-east-1:481665101132:secret:global_secrets-crxtcU"
}

data "aws_secretsmanager_secret_version" "global_secrets" {
  secret_id = data.aws_secretsmanager_secret.global_secrets.id
}

resource "aws_key_pair" "default_ssh_key" {
  key_name   = "default_ssh_key"
  public_key = jsondecode(data.aws_secretsmanager_secret_version.global_secrets.secret_string).ssh_public_key
}
