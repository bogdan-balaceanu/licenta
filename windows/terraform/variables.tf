variable "vsphere_user" {
   type = string
}

variable "vsphere_password" {
   type = string
}

variable "vsphere_server" {
   type = string
}

variable "windows_template" {
   type = string
}

variable "computer_name" {
   type = string
}

variable "vm_count" {
    type = number
}

variable "vm-name" {
  type        = string
  description = "The name of the vSphere virtual machines and the hostname of the machine"
}

variable "vm-cpu" {
  type        = string
  description = "Number of vCPU for the vSphere virtual machines"
}

variable "vm-ram" {
  type        = string
  description = "Amount of RAM for the vSphere virtual machines (example: 2048)"
}

variable "domain" {
  type        = string
  description = "Domain for DNS and AD"
}

variable "domain_admin_user" {
  type        = string
  description = "Domain account with necessary privileges to join a computer to the domain."
}

variable "domain_admin_password" {
  type        = string
  description = "Domain user password."
}

variable "dns_server_list" {
  type        = string
}

variable "ipv4_root" {
  type = string
}

variable "ipv4_start" {
  type = string
}

variable "ipv4_netmask" {
  type = number
}

variable "vmgateway" {
  type        = string
  description = "Network gateway IP"
}

variable "local_adminpass" {
  type        = string
  description = "admin pass local to machine"
}
