provider "vsphere" {
  user           = "${var.vsphere_user}"
  password       = "${var.vsphere_password}"
  vsphere_server = "${var.vsphere_server}"

  # If you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_virtual_machine" "base_template" {
  name          = "Ubuntu-1604-Template"
  datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
}

data "vsphere_datacenter" "vsdc" {
  name = "${var.virtual_datacenter_name}"
}

data "vsphere_compute_cluster" "vscc" {
  name          = "${var.virtual_cluster_name}"
  datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
}

data "vsphere_datastore_cluster" "vsdsc" {
  name          = "${var.datastore_cluster}"
  datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
}

# maybe you dont have a datastore cluster. make sure you change the instance settings too...
#
# data "vsphere_datastore" "vsds" {
#   name          = "${var.datastore}"
#   datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
# }

data "vsphere_network" "vnet_my_thing" {
  name          = "${var.my_vnet_name}"
  datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
}

