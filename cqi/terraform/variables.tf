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

variable "namecheap_username" {
  type = string
}

variable "namecheap_key" {
  type = string
}
