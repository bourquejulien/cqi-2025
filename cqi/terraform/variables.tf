variable "team_names" {
  description = "List of team names"
  type        = list(string)
  default = [
    "Polytechnique",
    "ETS",
    # "Concordia",
    # "McGill",
    # "UQTR",
    # "ULaval",
    # "UQAM",
    # "Sherbrooke",
    # "UQAC",
  ]
}

variable "domain" {
  description = "The server domain"
  type        = object({
    game_server = string
    game_runner = string
    address = string
  })
  default = {
    game_server = "data"
    game_runner = "runner"
    address = "cqiprog.info"
  }
}

variable "ec2_ssh_key" {
  description = "The server domain"
  type        = object({
    name = string
    public_key = string
  })
  default = {
    name = "default_ssh_key",
    public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIICQAOnBl4Y7WN4Zobf2lGkqvRYJzYpGlSfcjy0Z1n05 cqiprog@fastmail.com"
  }
}
