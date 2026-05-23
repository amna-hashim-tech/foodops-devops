terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  # Remote state stored in Azure Storage (best practice)
  backend "azurerm" {
    resource_group_name  = "foodops-tfstate-rg"
    storage_account_name = "foodopstfstate"
    container_name       = "tfstate"
    key                  = "foodops.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "foodops" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Azure Container Registry (stores Docker images)
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.foodops.name
  location            = azurerm_resource_group.foodops.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.foodops.location
  resource_group_name = azurerm_resource_group.foodops.name
  dns_prefix          = var.aks_cluster_name
  tags                = var.tags

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }

  # Enable Azure Monitor for containers
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.foodops.id
  }
}

# Grant AKS permission to pull images from ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}

# Log Analytics Workspace (for Azure Monitor)
resource "azurerm_log_analytics_workspace" "foodops" {
  name                = "${var.aks_cluster_name}-logs"
  location            = azurerm_resource_group.foodops.location
  resource_group_name = azurerm_resource_group.foodops.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}
