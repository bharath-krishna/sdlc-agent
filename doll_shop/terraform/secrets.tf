resource "kubernetes_secret" "db_secrets" {
  metadata {
    name      = "db-secrets"
    namespace = kubernetes_namespace.doll_shop.metadata[0].name
  }
  data = {
    "postgres-password" = var.postgres_password
  }
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "app-secrets"
    namespace = kubernetes_namespace.doll_shop.metadata[0].name
  }
  data = {
    "api-signature" = var.api_signature_text
  }
}
