provider "aws" {
  region     = var.aws_region
  profile    = var.aws_profile_name
  
  assume_role {
    role_arn = var.aws_assume_role_arn
  }
}

variable "instance_type" {
  description = "The EC2 instance type"
  type        = string
}

variable "subnet_id" {
  description = "The ID of the subnet in which to launch the EC2 instance"
  type        = string
  default     = "subnet-0adb07356e0c1c7fb"
}

variable "root_volume_size" {
  description = "The size of the root volume in GB"
  type        = number
}

variable "root_volume_type" {
  description = "The type of the root volume"
  type        = string
  default     = "gp2"
}

variable "data_volume_size" {
  description = "The size of the additional data volume in GB"
  type        = number
  default     = 50
}

variable "data_volume_type" {
  description = "The type of the additional data volume"
  type        = string
  default     = "gp2"
}

variable "ami_name" {
  description = "The name of the AMI to use for the EC2 instance"
  type        = string
  default     = "my-ami-name"
}

# variable "playbooks_directory" {
#   type        = string
#   description = "The relative path to the directory with all of the playbooks."
#   sensitive   = false
#   default     = "/home/syscfgmgr/playbooks" # The playbooks are bundled with the gitlab-terraform image.
# }

variable "ssh_username" {
  description = "The SSH username for Ansible"
  type        = string
  default     = "syscfgmgr"
}

variable "aws_profile_name" {
  description = "AWS profile name"
  type        = string
}

variable "aws_assume_role_arn" {
  description = "AWS ARN for the assumed role"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "instance_count" {
  type        = number
  description = "The number of instances to deploy."
  
  validation {
    condition     = var.instance_count <= 3
    error_message = "The instance count must not exceed 3."
  }
}

variable "system_owner_name" {
  type        = string
  description = "Name of the system owner"
}

variable "system_owner_email" {
  type        = string
  description = "Email address of the system owner"
}

variable "gitlab_project" {
  type        = string
  description = "Name of the GitLab project"
}

variable "gitlab_project_pipeline" {
  type        = string
  description = "GitLab project pipeline"
}

variable "gitlab_project_branch" {
  type        = string
  description = "GitLab project branch"
}

variable "line_office" {
  type        = string
  description = "Line office"
}

variable "environment_tag" {
  type        = string
  description = "Environment tag"
}

variable "fisma_tag" {
  type        = string
  description = "The fisma id tag."
  default     = "6702"
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

variable "account_tag" {
  type        = string
  description = "The AWS account tag in the vSphere environment"
  default     = "ERMA"
}

variable "application_name" {
  type        = string
  description = "Application name"
}

variable "division" {
  type        = string
  description = "Division"
}

variable "program" {
  type        = string
  description = "Program office"
}

variable "program_manager" {
  type        = string
  description = "Program office manager"
}

variable "security_group_id" {
  type        = string
  description = "The ID for the security group to apply to the ec2 instance."
  default     = "sg-0bf339447849a554e"
}

variable "rhel_org_id" {
  type        = string
  description = "Used for registering the OS with RHEL."
  default     = "16962152"
}

variable "rhel_activation_key" {
  type        = string
  description = "Used for registering the OS with RHEL."
  default     = "Production"
}

variable "cloudwatch_agent_ssm_key" {
  type        = string
  description = "The cloudwatch configuration file, which is stored in an SSM paramter."
  default     = "/us-west-2/dev/cw/agent/ec2-config"
}

variable "iam_instance_profile_name" {
  type        = string
  description = "The name of the IAM EC2 instance role to attach to the EC2 instance."
  default     = "IAMStackEC2InstanceProfile"
}

# GitLab Backend
terraform {
  backend "http" {
  }
}

module "amazon" {
  source = "gitlab.orr.noaa.gov/internal-terraform-module-registry/amazon/ec2s"
  version = "0.3.1"

  count                     = var.instance_count
  vm_name                   = "${lower(var.line_office)}-${lower(var.program)}-${lower(var.application_name)}${count.index + 1}-6702"
  instance_type             = var.instance_type
  subnet_id                 = var.subnet_id
  root_volume_size          = var.root_volume_size
  root_volume_type          = var.root_volume_type
  data_volume_size          = var.data_volume_size
  data_volume_type          = var.data_volume_type
  ami_name                  = var.ami_name
  ssh_username              = var.ssh_username
  aws_profile_name          = var.aws_profile_name
  aws_assume_role_arn       = var.aws_assume_role_arn
  aws_region                = var.aws_region
  system_owner_name         = var.system_owner_name
  system_owner_email        = var.system_owner_email
  gitlab_project            = var.gitlab_project
  gitlab_project_pipeline   = var.gitlab_project_pipeline
  gitlab_project_branch     = var.gitlab_project_branch
  line_office               = var.line_office
  environment_tag           = var.environment_tag
  role_tag                  = var.role_tag
  os_tag                    = var.os_tag
  account_tag               = var.account_tag
  fisma_tag                 = var.fisma_tag
  application_name          = var.application_name
  division                  = var.division
  program                   = var.program
  program_manager           = var.program_manager
  security_group_id         = var.security_group_id
  rhel_org_id               = var.rhel_org_id
  rhel_activation_key       = var.rhel_activation_key
  cloudwatch_agent_ssm_key  = var.cloudwatch_agent_ssm_key
  iam_instance_profile_name = var.iam_instance_profile_name
}