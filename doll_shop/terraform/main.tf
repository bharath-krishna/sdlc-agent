terraform {
  required_version = ">= 1.0.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  # This defaults to looking for a config file at ~/.kube/config
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "doll_shop" {
  metadata {
    name = var.namespace
  }
}
