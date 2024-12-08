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
