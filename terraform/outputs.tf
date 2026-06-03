output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.foodops.name
}

output "kube_config" {
  description = "Kubeconfig for connecting to AKS"
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive   = true
}

output "namespaces" {
  description = "The three environment namespaces"
  value = {
    dev        = kubernetes_namespace.dev.metadata[0].name
    staging    = kubernetes_namespace.staging.metadata[0].name
    production = kubernetes_namespace.production.metadata[0].name
  }
}
