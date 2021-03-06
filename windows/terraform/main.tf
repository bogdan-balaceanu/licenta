terraform {
  required_providers {
    vsphere = {
      source = "hashicorp/vsphere"
      version = "2.1.1"
    }
  }
}

provider "vsphere" {
  vim_keep_alive = 30
  user           = var.vsphere_user
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server

  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = "Datacenter1"
}

data "vsphere_datastore" "datastore" {
  name          = "Datastore2"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = "Cluster1"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = "VM Network"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = var.windows_template
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_virtual_machine" "vm" {
  count = "${var.vm_count}"

  name             = "${var.vm-name}-${count.index + 1}"
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id


  num_cpus                   = var.vm-cpu
  memory                     = var.vm-ram
  guest_id                   = data.vsphere_virtual_machine.template.guest_id
  scsi_type                  = data.vsphere_virtual_machine.template.scsi_type
  wait_for_guest_net_timeout = -1

  network_interface {
    network_id   = data.vsphere_network.network.id
    adapter_type = "vmxnet3"
  }

  disk {
    label             = "machine.vmdk"
    thin_provisioned = true
    eagerly_scrub    = false
    size             = data.vsphere_virtual_machine.template.disks.0.size
  }

  disk {
    label             = "machine_1.vmdk"
    unit_number      = 1
    thin_provisioned = true
    eagerly_scrub    = false
    size             = data.vsphere_virtual_machine.template.disks.0.size
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id

    customize {
      windows_options {
        computer_name = "${var.vm-name}-${count.index + 1}"
        join_domain           = var.domain
        domain_admin_user     = var.domain_admin_user
        domain_admin_password = var.domain_admin_password
        admin_password        = var.local_adminpass
      }
      network_interface {
        ipv4_address    = "${var.ipv4_root}${var.ipv4_start + count.index}"
        ipv4_netmask    = "${var.ipv4_netmask}"
        dns_server_list = [ "${var.dns_server_list}" ]
        dns_domain      = "${var.domain}"
      }
      ipv4_gateway = "${var.vmgateway}"
      timeout = 30

    }

  }
}


