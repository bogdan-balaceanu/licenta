variable "vsphere_user" { 
   default = "administrator@vsphere.local"
}

variable "vsphere_password" {
   default = "L!nux123"
}

variable "vsphere_server" {
   default = "VCSA.licente.atm"
}

variable "windows_template" {
    default = "Win2016-Template"
}

variable "computer_name" {
    default = "machine"
}

variable "vm_count" {
    type = number
    default = 1
}

variable "vm-name" {
  type        = string
  description = "The name of the vSphere virtual machines and the hostname of the machine"
  default = "vm-name"
}

variable "vm-cpu" {
  type        = string
  description = "Number of vCPU for the vSphere virtual machines"
  default     = "2"
}

variable "vm-ram" {
  type        = string
  description = "Amount of RAM for the vSphere virtual machines (example: 2048)"
  default = "4096"
}

variable "domain" {
  type        = string
  description = "Domain for DNS and AD"
  default = "10.230.30.111"
}

variable "domain_admin_user" {
  type        = string
  description = "Domain account with necessary privileges to join a computer to the domain."
  default = "administrator@vsphere.local"
}

variable "domain_admin_password" {
  type        = string
  description = "Domain user password."
  default = "L!nux123"
}

variable "dns_server_list" {
  type        = list(any)
  description = "list of DNS server IPs"
  default = ["10.230.30.111"]
}

variable "ipv4_root" {
  default = "10.230.30."
}

variable "ipv4_start" {
  default = "60"
}

variable "vmgateway" {
  type        = string
  description = "Network gateway IP"
  default = "10.230.30.1"
}

variable "local_adminpass" {
  type        = string
  description = "admin pass local to machine"
  default = "S3cr3t!"
}
