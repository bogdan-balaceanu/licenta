variable "vsphere_user" {
  type = string
}
variable "vsphere_password" {
  type = string
}

variable "vsphere_server" {
  type = string
}

variable "virtual_datacenter_name" {
  type = string
}

variable "virtual_cluster_name" {
  type = string
}

variable "datastore_cluster" {
  type = string
}

variable "vm_folder" {
  type = string
  description = "The name of the folder where the VM's will be created"
}

variable "my_vnet_name" {
  type = string
}


variable "dns_server_1" {
  type = string
}


variable "vm_count" {
  type = number
}
variable "ipv4_root" {
  type = string
}
variable "ipv4_start" {
  type = string
}

variable "ipv4_gateway" {
  type = string
}

variable "ipv4_netmask" {
  type = number
}

variable "vm_name" {
  type = string
}

variable "num_cpus" {
  type = number
}

variable "vm_memory" {
  type = number
}

variable "vm_template_name" {
  type = string
}
