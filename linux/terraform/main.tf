provider "vsphere" {
  user           = "${var.vsphere_user}"
  password       = "${var.vsphere_password}"
  vsphere_server = "${var.vsphere_server}"

  allow_unverified_ssl = true
}

data "vsphere_virtual_machine" "base_template" {
  name          = "${var.vm_template_name}"
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


data "vsphere_network" "vnet_my_thing" {
  name          = "${var.my_vnet_name}"
  datacenter_id = "${data.vsphere_datacenter.vsdc.id}"
}


resource "vsphere_virtual_machine" "my_vm" {
  count	         = "${var.vm_count}"
  name                   = "${var.vm_name}-${count.index + 1}"
  annotation             = "My VM"
  folder                 = "/${var.vm_folder}"
  resource_pool_id       = "${data.vsphere_compute_cluster.vscc.resource_pool_id}"
  datastore_cluster_id   = "${data.vsphere_datastore_cluster.vsdsc.id}"
  cpu_hot_add_enabled    = true
  memory_hot_add_enabled = true
  cpu_hot_remove_enabled = false
  enable_logging         = true
  boot_retry_delay       = 10

  num_cpus  = "${var.num_cpus}"
  memory    =  "${var.vm_memory}"
  guest_id  = "${data.vsphere_virtual_machine.base_template.guest_id}"
  scsi_type = "${data.vsphere_virtual_machine.base_template.scsi_type}"

  network_interface {
    network_id   = "${data.vsphere_network.vnet_my_thing.id}"
    adapter_type = "${data.vsphere_virtual_machine.base_template.network_interface_types[0]}"  
  }

  cdrom {
      client_device = true
  }
  disk {
    label            = "disk0"
    size             = "${data.vsphere_virtual_machine.base_template.disks.0.size}"
    eagerly_scrub    = "${data.vsphere_virtual_machine.base_template.disks.0.eagerly_scrub}"
    thin_provisioned = "${data.vsphere_virtual_machine.base_template.disks.0.thin_provisioned}"
  }
  wait_for_guest_net_timeout = 30

  clone {
    template_uuid = "${data.vsphere_virtual_machine.base_template.id}"
    customize {
      timeout     = 10
      linux_options {
        host_name = "${var.vm_name}-${count.index + 1}"
	domain = "licente.atm"
      }
      network_interface {
        ipv4_address = "${var.ipv4_root}${var.ipv4_start + count.index}"
        ipv4_netmask = "${var.ipv4_netmask}"
      }
      dns_server_list = [ "${var.dns_server_1}" ]
      ipv4_gateway    = "${var.ipv4_gateway}"
    }
  }
}
