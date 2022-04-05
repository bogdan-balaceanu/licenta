variable "vsphere_user" {
  default = "administrator@vsphere.local"
}

variable "vsphere_password" {
  default = "L!nux123"
}

variable "vsphere_server" {
  default = "VCSA.licente.atm"
}

variable "virtual_datacenter_name" {
  default = "Datacenter1"
}

variable "virtual_cluster_name" {
  default = "Cluster1"
}

variable "datastore_cluster" {
  default = "DatastoreCluster1"
}

variable "vm_folder" {
  default = "VM_Folder"
}

variable "my_vnet_name" {
  default = "VM Network"
}


variable "dns_server_1" {
  default = "10.230.30.111"
}

variable "dns_server_2" {
  default = ""
}

variable "vm_count" {
  type = number
  default = 1
}
variable "ipv4_root" {
  default = "10.230.30."
}
variable "ipv4_start" {
  default = "40"
}
