provider "vsphere" {
  user                 = var.vmware_username
  password             = var.vmware_password
  vsphere_server       = var.vmware_fqdn
  allow_unverified_ssl = var.vmware_allow_unverified_ssl
}

variable "instance_count" {
  type = number
}

variable "vm_cpu_cores" {
  type = number
}

variable "vm_cpu_cores_per_socket" {
  type = number
}

variable "vm_memory" {
  type = number
}

variable "vmware_fqdn" {
  type = string
}

variable "vmware_datastore" {
  type = string
}

variable "vmware_cluster" {
  type = string
}

variable "vmware_resource_pool" {
  type = string
}

variable "vmware_allow_unverified_ssl" {
  type = bool
}

variable "vmware_datacenter" {
  type = string
}

variable "vmware_username" {
  type = string
}

variable "vmware_password" {
  type = string
}

variable "environment" {
  type = string
}

variable "vm_firmware" {
  type = string
}

variable "vm_secure_boot" {
  type = bool
}

variable "vm_folder" {
  type = string
}

variable "vm_nested_virt_enabled" {
  type = bool
}

variable "vm_mem_hot_add" {
  type = bool
}

variable "vm_cpu_hot_add" {
  type = bool
}

variable "vm_notes" {
  type = string
}

variable "vm_network" {
  type = string
}

variable "vm_disk_size" {
  type = number
}

variable "vm_data_disk_size" {
  type = number
}

variable "vm_template_name" {
  type = string
}

variable "os_domain_name" {
  type = string
}

variable "ssh_username" {
  type = string
}

variable "content_library_name" {
  type = string
}

variable "vm_template_type" {
  type = string
}

variable "system_owner_name" {
  type        = string
  description = "The system owner's name in the vSphere environment"
}

variable "system_owner_email" {
  type        = string
  description = "The system owner's email in the vSphere environment"
}

variable "division" {
  type        = string
  description = "The division in the vSphere environment"
}

variable "line_office" {
  type        = string
  description = "The line_office in the vSphere environment"
}

variable "environment_tag" {
  type        = string
  description = "The environment tag in the vSphere environment"
}

variable "fisma_tag" {
  type        = string
  description = "The fisma id tag."
  default     = "6701"
}

variable "os_tag" {
  type        = string
  description = "The os tag in the vSphere environment"
  default     = "RHEL8"
}

variable "role_tag" {
  type        = string
  description = "The role tag in the vSphere environment"
  default     = "Default"
}

variable "application_name" {
  type        = string
  description = "The application name in the vSphere environment"
}

variable "gitlab_project" {
  type        = string
  description = "The GitLab project in the vSphere environment"
}

variable "gitlab_project_branch" {
  type        = string
  description = "The GitLab project branch in the vSphere environment"
}

variable "program" {
  type        = string
  description = "The program in the vSphere environment"
}

variable "program_manager" {
  type        = string
  description = "The program manager in the vSphere environment"
}

variable "gitlab_project_pipeline" {
  type        = string
  description = "The URL for the pipeline details"
}

terraform {
  backend "http" {
  }
}

locals {
  line_office = "${lower(var.line_office)}"
  program     = "${lower(var.program)}"
  application_name = "${lower(var.application_name)}"
}

module "vsphere" {
  source = "gitlab.orr.noaa.gov/internal-terraform-module-registry/vsphere/vms"
  version = "0.1.0"

  count                         = var.instance_count
  vm_name                       = "${local.line_office}-${local.program}-${local.application_name}${count.index + 1}-6701"
  vm_cpu_cores                  = var.vm_cpu_cores
  vm_cpu_cores_per_socket       = var.vm_cpu_cores_per_socket
  vm_memory                     = var.vm_memory
  vmware_fqdn                   = var.vmware_fqdn
  vmware_datastore              = var.vmware_datastore
  vmware_cluster                = var.vmware_cluster
  vmware_resource_pool          = var.vmware_resource_pool
  vmware_allow_unverified_ssl   = var.vmware_allow_unverified_ssl
  vmware_datacenter             = var.vmware_datacenter
  vmware_username               = var.vmware_username
  vmware_password               = var.vmware_password
  environment                   = var.environment
  vm_firmware                   = var.vm_firmware
  vm_secure_boot                = var.vm_secure_boot
  vm_folder                     = var.vm_folder
  vm_nested_virt_enabled        = var.vm_nested_virt_enabled
  vm_mem_hot_add                = var.vm_mem_hot_add
  vm_cpu_hot_add                = var.vm_cpu_hot_add
  vm_notes                      = var.vm_notes
  vm_network                    = var.vm_network
  vm_disk_size                  = var.vm_disk_size
  vm_data_disk_size             = var.vm_data_disk_size
  vm_template_name              = var.vm_template_name
  os_domain_name                = var.os_domain_name
  ssh_username                  = var.ssh_username
  content_library_name          = var.content_library_name
  vm_template_type              = var.vm_template_type
  system_owner_name             = var.system_owner_name
  system_owner_email            = var.system_owner_email
  division                      = var.division
  line_office                   = var.line_office
  environment_tag               = var.environment_tag
  role_tag                      = var.role_tag
  os_tag                        = var.os_tag
  fisma_tag                     = var.fisma_tag
  application_name              = var.application_name
  gitlab_project                = var.gitlab_project
  gitlab_project_branch         = var.gitlab_project_branch
  program                       = var.program
  program_manager               = var.program_manager
  gitlab_project_pipeline       = var.gitlab_project_pipeline
}
