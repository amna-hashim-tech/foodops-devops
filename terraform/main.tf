terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
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

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config[0].host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate)
}

# ─── RESOURCE GROUP ───
resource "azurerm_resource_group" "foodops" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ─── AZURE CONTAINER REGISTRY ───
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.foodops.name
  location            = azurerm_resource_group.foodops.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# ─── LOG ANALYTICS ───
resource "azurerm_log_analytics_workspace" "foodops" {
  name                = "${var.aks_cluster_name}-logs"
  location            = azurerm_resource_group.foodops.location
  resource_group_name = azurerm_resource_group.foodops.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# ─── AKS CLUSTER ───
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.foodops.location
  resource_group_name = azurerm_resource_group.foodops.name
  dns_prefix          = var.aks_cluster_name
  tags                = var.tags

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.foodops.id
  }
}

# ─── GIVE AKS PERMISSION TO PULL FROM ACR ───
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}

# ─── THREE KUBERNETES NAMESPACES ───
resource "kubernetes_namespace" "dev" {
  metadata {
    name = "foodops-dev"
    labels = {
      environment = "dev"
      project     = "foodops"
    }
  }
  depends_on = [azurerm_kubernetes_cluster.aks]
}

resource "kubernetes_namespace" "staging" {
  metadata {
    name = "foodops-staging"
    labels = {
      environment = "staging"
      project     = "foodops"
    }
  }
  depends_on = [azurerm_kubernetes_cluster.aks]
}

resource "kubernetes_namespace" "production" {
  metadata {
    name = "foodops-prod"
    labels = {
      environment = "production"
      project     = "foodops"
    }
  }
  depends_on = [azurerm_kubernetes_cluster.aks]
}
