resource "aws_db_instance" "default" {
    identifier           = "main-server-database"
    allocated_storage    = 20
    db_name              = "postgres"
    storage_type         = "gp2"
    engine               = "postgres"
    engine_version       = "17.2"
    instance_class       = "db.t3.micro"
    username             = "postgres"
    password             =  data.aws_secretsmanager_random_password.database_password.random_password
    publicly_accessible  = true
    skip_final_snapshot  = true

    vpc_security_group_ids = [aws_security_group.db.id]
}

data "aws_secretsmanager_random_password" "database_password" {
  password_length     = 30
  include_space       = false
  exclude_punctuation = true
}

resource "aws_secretsmanager_secret" "database" {
  name                           = "database"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id     = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
                    username = aws_db_instance.default.username
                    password = aws_db_instance.default.password
                    db_name  = aws_db_instance.default.db_name
                    identifier = aws_db_instance.default.identifier
                })
}

resource "aws_security_group" "db" {
    name        = "db_security_group"
    description = "Allow access to the database from EC2 instances"

    ingress {
        from_port   = 5432
        to_port     = 5432
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

resource "aws_security_group_rule" "allow_postgres" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.db.id
  source_security_group_id = var.ec2_security_group_id
}
