#!/bin/sh
sudo terraform init
#modul asta este doar din terraform apply , care isi creaza singur un plan si il aplica
#terraform plan -var vm_count=$1 -out=plan
#terraform apply -input=false -var vm_count=$1 -auto-approve

#modul asta e din 2 pasi , se face prima oara un plan , se salveaza intr-un fisier
#si acel fisier se da ca input pentru terraform apply
#asa am gasit pe net ca se face pentru "terraform automation" gen best practice

sudo terraform plan -var vm_count=$1 -out=plan -lock=false
sudo terraform apply "plan" 
