resource "kubernetes_deployment" "doll_shop_api" {
  metadata {
    name      = "doll-shop-api"
    namespace = kubernetes_namespace.doll_shop.metadata[0].name
  }
  spec {
    replicas = 2
    selector {
      match_labels = {
        app = "doll-shop-api"
      }
    }
    template {
      metadata {
        labels = {
          app = "doll-shop-api"
        }
      }
      spec {
        container {
          name  = "api"
          image = var.app_image
          port {
            container_port = 9999
          }
          env {
            name  = "POSTGRES_HOST"
            value = "postgres"
          }
          env {
            name  = "POSTGRES_PORT"
            value = "5432"
          }
          env {
            name  = "POSTGRES_DB"
            value = "dollshop"
          }
          env {
            name  = "POSTGRES_USERNAME"
            value = "postgres"
          }
          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_secrets.metadata[0].name
                key  = "postgres-password"
              }
            }
          }
          env {
            name = "API_SIGNATURE_TEXT"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "api-signature"
              }
            }
          }
          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }
          liveness_probe {
            http_get {
              path = "/docs"
              port = 9999
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
          readiness_probe {
            http_get {
              path = "/docs"
              port = 9999
            }
            initial_delay_seconds = 15
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "doll_shop_api" {
  metadata {
    name      = "doll-shop-api"
    namespace = kubernetes_namespace.doll_shop.metadata[0].name
  }
  spec {
    selector = {
      app = "doll-shop-api"
    }
    port {
      port        = 80
      target_port = 9999
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_ingress_v1" "doll_shop_ingress" {
  metadata {
    name      = "doll-shop-ingress"
    namespace = kubernetes_namespace.doll_shop.metadata[0].name
  }
  spec {
    rule {
      host = var.ingress_host
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.doll_shop_api.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
