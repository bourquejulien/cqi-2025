resource "aws_instance" "game_runner" {
  ami                         = "ami-0e2c8caa4b6378d8c" # "ami-0325498274077fac5" Ubuntu 24.04 ARM_64 / "ami-0e2c8caa4b6378d8c" Ubuntu 24.04 X86_64
  instance_type               = "m5a.2xlarge" # "t4g.small" / "m5a.xlarge" or "m5a.2xlarge"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.game_runner_sg.id]
  key_name                    = var.ssh_key_name

  iam_instance_profile = var.instance_profile_name

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = base64decode(nonsensitive(var.global_secrets.ssh_private_key))
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
      "curl -s 'https://dynamicdns.park-your-domain.com/update?host=${var.domain.game_runner}${var.instance_number}&domain=${var.domain.address}&password=${nonsensitive(var.global_secrets.namecheap_key)}&ip=${self.public_ip}'",
      "sudo GITHUB_TOKEN='${nonsensitive(var.global_secrets.github_token)}' ./init.sh",
    ]
  }

  root_block_device {
    volume_size = 64
  }

  tags = {
    Name = "game_runner_${var.instance_number}"
  }
}

resource "aws_security_group" "game_runner_sg" {
  name_prefix = "game_runner_sg_${var.instance_number}"

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
