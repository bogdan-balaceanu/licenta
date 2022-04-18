import subprocess
import os
import re
import json
from argparse import ArgumentParser

playbooks_map = {
    "vscode": "install_vscode.yml",
    "notepad++": "install_npp.yml",
    "dnspy": "install_dnspy.yml",
    "putty": "install_putty.yml",
    "winscp": "install_winscp.yml",
    "wireshark": "install_wireshark.yml"
}

LINUX_ANSIBLE_HOSTS_FILE = "./linux/ansible/hosts"
WINDOWS_ANSIBLE_HOSTS_FILE = "./windows/ansible/hosts"

def generate_terraform_artefacts(config):
    operating_system = config['operating-system']
    print(operating_system)
    if operating_system != "Linux" and operating_system != "Windows":
        print("Operating system field must be \"Linux\" or \"Windows\". Please re-write the config file.")
        exit()


    elif operating_system == "Linux":
        print("E linux")

        os.mkdir("/home/bala/Desktop/temp")     
        subprocess.call('cp /home/bala/Desktop/de_mutat/licenta/linux/terraform/terraform.tfvars /home/bala/Desktop/temp', shell = True)
        
        with open('./linux/terraform/terraform.tfvars'.format(config),'r') as file:
            tfvars_file = file.read()
            print(tfvars_file.format(**config))
                
        with open('./linux/terraform/terraform.tfvars', 'w+') as f_out:
            f_out.write(tfvars_file.format(**config))

        old_cwd = os.getcwd()
        os.chdir("./linux/terraform")

        #subprocess.call('terraform init && terraform plan -out plan&& terraform apply "plan"', shell = True)
        subprocess.call('terraform destroy --auto-approve', shell = True)
        
        os.chdir(old_cwd)

        subprocess.call('cp /home/bala/Desktop/temp/terraform.tfvars /home/bala/Desktop/de_mutat/licenta/linux/terraform/terraform.tfvars', shell = True)

        subprocess.call('rm -rf /home/bala/Desktop/temp', shell = True)


    elif operating_system == "Windows":
        print("E windows")

        os.mkdir("/home/bala/Desktop/temp")     
        subprocess.call('cp /home/bala/Desktop/de_mutat/licenta/windows/terraform/terraform.tfvars /home/bala/Desktop/temp', shell = True)
        
        with open('./windows/terraform/terraform.tfvars'.format(config),'r') as file:
            tfvars_file = file.read()
                
        with open('./windows/terraform/terraform.tfvars', 'w+') as f_out:
            f_out.write(tfvars_file.format(**config))
        
        old_cwd = os.getcwd()
        os.chdir("./windows/terraform")

        subprocess.call('terraform init && terraform plan -out plan&& terraform apply "plan"', shell = True)
        #subprocess.call('terraform destroy', shell = True)
        
        os.chdir(old_cwd)
        
        subprocess.call('cp /home/bala/Desktop/temp/terraform.tfvars /home/bala/Desktop/de_mutat/licenta/windows/terraform/terraform.tfvars', shell = True)

        subprocess.call('rm -rf /home/bala/Desktop/temp', shell = True)

        print("GATA")


def generate_ansible_host_file(config):
    if len(config['toolset']) == 0:
        print("No tools need to be installed")
        quit() #sau exit

    operating_system = config['operating-system']
    if operating_system == "Linux":
        f_out = open(LINUX_ANSIBLE_HOSTS_FILE,"w")
        f_out.write("[linuxvms]\n")
        after = " ansible_user=kopicloud ansible_password=kopicloud\n"
        for i in range(int(config['vm-count'])):
            f_out.write(str(config['vm-ipv4-root']) + str(int(int(config['vm-ipv4-start']) + int(i))) + after)
        f_out.close()
    elif operating_system == "Windows":
        print(config['vm-count'])
        f_out = open(WINDOWS_ANSIBLE_HOSTS_FILE,"w")
        f_out.write("[winhosts]\n")
        after = " ansible_user=Administrator ansible_password=S3cr3t! ansible_connection=winrm ansible_winrm_transport=basic ansible_winrm_server_cert_validation=ignore\n"
        for i in range(int(config['vm-count'])):
            f_out.write(str(config['vm-ipv4-root']) + str(int(int(config['vm-ipv4-start']) + int(i))) + after)
        f_out.close()



def install_toolset(config):

       
    print("Wait until the success message is shown")
    operating_system = config['operating-system']
    if operating_system == "Linux":


        cmd = "ansible-playbook -i linux/ansible/hosts linux/ansible/playbook.yml --extra-vars=\'{\"tools\":" + str(config['toolset']) + "}\'" 

        os.system(cmd)

        print("Tool installation is complete")
        print("Now the VMs are created and the toolset is already installed on them")
    elif operating_system == "Windows":
        print("Wait until the success message is shown")

        # install 7zip
        cmd = "ansible-playbook -i windows/ansible/hosts windows/ansible/playbooks/install_7zip.yml"
        os.system(cmd)

        for tool in config['toolset']:
            cmd = "ansible-playbook -i windows/ansible/hosts windows/ansible/playbooks/" + playbooks_map[tool]
            os.system(cmd)

        print("The toolset you chose has been successfully installed on the VMs.")


def checkResources(args):

    for arg in args.config:        
        with open(arg, 'r') as f_config:
            config = json.load(f_config)
            if(config['operating-system'] != "Windows" and config['operating-system'] != "Linux"):
                print("Wrong operating-system in file " + str(arg) + ". It must be \"Windows\" or \"Linux\"")


if __name__ == '__main__':
    parser = ArgumentParser(description = 'This module is used to automatically deploy a Windows/Linux infrastructure')
    parser.add_argument('-c', '--config', nargs='+', help = 'Relative path to configuration file', required = True)
    args = parser.parse_args()

    checkResources(args)
    

    for arg in args.config:        
        print(arg)
        with open(arg, 'r') as f_config:
            config = json.load(f_config)
            #print(config['vm-count'])
            #print(config)
            
            generate_terraform_artefacts(config)
            generate_ansible_host_file(config)
            install_toolset(config)

    print("S-a terminat..")
    