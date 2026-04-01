output "api_service_name" {
  value = kubernetes_service.doll_shop_api.metadata[0].name
}

output "database_host" {
  value = kubernetes_service.postgres.metadata[0].name
}

output "ingress_url" {
  value = "http://${var.ingress_host}"
}
