variable "namespace" {
  description = "Kubernetes namespace to deploy into"
  type        = string
  default     = "doll-shop"
}

variable "app_image" {
  description = "Docker image for the Doll Shop API"
  type        = string
  default     = "doll-shop-api:latest"
}

variable "ingress_host" {
  description = "Hostname for the application ingress"
  type        = string
  default     = "dollshop.krishb.in"
}

variable "postgres_password" {
  description = "Password for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "api_signature_text" {
  description = "JWT Signing Key"
  type        = string
  sensitive   = true
}
