#!/bin/sh
sudo terraform init
sudo terraform plan -var vm_count=$1 -out=plan -lock=false
sudo terraform apply "plan"
