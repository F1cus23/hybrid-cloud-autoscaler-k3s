terraform {
  backend "azurerm" {
    resource_group_name  = "TerraformState-RG-Sweden"
    storage_account_name = "tfstateficus99"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "admin_password" {
  description = "Parola userului azureuser de pe VM-urile din Azure"
  type        = string
  sensitive   = true
}

variable "tailscale_auth_key" {
  description = "Cheie de autentificare Tailscale (tskey-auth-...) pentru VM-urile noi"
  type        = string
  sensitive   = true
}

variable "redis_host" {
  description = "IP-ul Tailscale al nodului K3s unde ruleaza Redis"
  type        = string
}

variable "redis_port" {
  description = "NodePort-ul serviciului redis-extern"
  type        = number
  default     = 30474
}

variable "imagine_muncitor" {
  description = "Imaginea Docker a muncitorului"
  type        = string
  default     = "ovidiuu/muncitor-tpi:v7"
}

variable "numar_masini" {
  description = "Numarul de masini pornite simultan in cloud"
  type        = number
  default     = 0
}

# 1. Creăm un grup de resurse proaspăt pentru muncitori
resource "azurerm_resource_group" "rg_muncitori" {
  name     = "Muncitori-Cloud-RG"
  location = "swedencentral"
}

# 2. Creăm Rețeaua și Subnet-ul
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-muncitori"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg_muncitori.location
  resource_group_name = azurerm_resource_group.rg_muncitori.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-muncitori"
  resource_group_name  = azurerm_resource_group.rg_muncitori.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

# 3. Creăm IP-uri Publice și Plăci de rețea (multiplicate cu 'count')
resource "azurerm_public_ip" "pip" {
  count               = var.numar_masini
  name                = "pip-muncitor-${count.index}"
  location            = azurerm_resource_group.rg_muncitori.location
  resource_group_name = azurerm_resource_group.rg_muncitori.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "nic" {
  count               = var.numar_masini
  name                = "nic-muncitor-${count.index}"
  location            = azurerm_resource_group.rg_muncitori.location
  resource_group_name = azurerm_resource_group.rg_muncitori.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip[count.index].id
  }
}

# 4. Creăm Mașinile Virtuale (Rezolvă problema cu os_disk și nic)
resource "azurerm_linux_virtual_machine" "muncitor_cloud" {
  count               = var.numar_masini
  name                = "azure-worker-${count.index}"
  resource_group_name = azurerm_resource_group.rg_muncitori.name
  location            = azurerm_resource_group.rg_muncitori.location
  size                = "Standard_B2ats_v2"
  admin_username      = "azureuser"
  
  # Folosim parola in loc de chei SSH complicate (Tailscale ne protejeaza oricum)
  disable_password_authentication = false
  admin_password                  = var.admin_password

  network_interface_ids = [
    azurerm_network_interface.nic[count.index].id,
  ]

  # Aici definim Hard Disk-ul lipsa
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  # Aici ii spunem sa instaleze Ubuntu 22.04
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  custom_data = base64encode(<<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    
    curl -fsSL https://tailscale.com/install.sh | sh
    tailscale up --authkey=${var.tailscale_auth_key}
    
    # Pornim 2 containere
    docker run -d --network host -e REDIS_HOST=${var.redis_host} -e REDIS_PORT=${var.redis_port} --name muncitor-1 ${var.imagine_muncitor}
    docker run -d --network host -e REDIS_HOST=${var.redis_host} -e REDIS_PORT=${var.redis_port} --name muncitor-2 ${var.imagine_muncitor}
  EOF
  )
}
