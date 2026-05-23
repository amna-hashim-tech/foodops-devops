variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "foodops-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "UAE North"
}

variable "acr_name" {
  description = "Azure Container Registry name (must be globally unique)"
  type        = string
  default     = "foodopsacr"
}

variable "aks_cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "foodops-aks"
}

variable "node_count" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 2
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    project     = "foodops"
    environment = "production"
    owner       = "amna"
  }
}
