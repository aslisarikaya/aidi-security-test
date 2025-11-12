variable "exoscale_api_key" {
  type        = string
  description = "Exoscale API key"
  sensitive   = true
}

variable "exoscale_api_secret" {
  type        = string
  description = "Exoscale API secret"
  sensitive   = true
}

variable "ssh_public_key" {
  type        = string
  description = "Your local SSH public key"
}

variable "zone" {
  type        = string
  description = "Exoscale zone (e.g., ch-dk-2)"
  default     = "ch-dk-2"
}

variable "instance_type" {
  type        = string
  description = "Instance type"
  default     = "standard.small"
}

variable "instance_name" {
  type        = string
  default     = "currency-conversion-vm"
}

variable "template_name" {
  type        = string
  description = "Template to use (Ubuntu 22.04)"
  default     = "Linux Ubuntu 22.04 LTS 64-bit"
}
