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
    main_server = string
    game_runner = string
    address = string
  })
  default = {
    main_server = "server"
    game_runner = "runner"
    address = "cqiprog.info"
  }
}
