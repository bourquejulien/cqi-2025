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
    name = string
    host = string
  })
  default = {
    host = "data"
    name = "cqiprog.info"
  }
}
