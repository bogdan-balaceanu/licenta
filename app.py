import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from pyVmomi import vim
from pyVim import connect
import subprocess
import sys
import os
import re
import json
import shutil
from argparse import ArgumentParser

playbooks_map = {
    "firefox": "install_firefox.yml",
    "notepad++": "install_npp.yml",
    "dnspy": "install_dnspy.yml",
    "putty": "install_putty.yml",
    "winscp": "install_winscp.yml",
    "wireshark": "install_wireshark.yml"
}

TOTAL_VMS_ALLOWED = 15
TOTAL_RAM_ALLOWED_ON_A_SINGLE_VM = 4096

LINUX_ANSIBLE_HOSTS_FILE = "./linux/ansible/hosts"
WINDOWS_ANSIBLE_HOSTS_FILE = "./windows/ansible/hosts"

def generate_terraform_artefacts(config,tfvars_config):
    operating_system = config['vm-info']['operating-system']
    os.mkdir("/home/bala/Desktop/temp")  
    old_cwd = os.getcwd()  

    if operating_system == "Linux":
        subprocess.call('cp /home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars /home/bala/Desktop/temp', shell = True)

        with open('./linux/terraform/terraform.tfvars'.format(config),'r') as file:
            tfvars_file = file.read()            
                
        with open('./linux/terraform/terraform.tfvars', 'w+') as f_out:
            f_out.write(tfvars_file.format(**tfvars_config))
            
        os.chdir("./linux/terraform")
        subprocess.call('terraform init && terraform plan -out plan&& terraform apply "plan"', shell = True)
        shutil.copyfile('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraformLastState.tfvars')
        os.chdir(old_cwd)

        subprocess.call('cp /home/bala/Desktop/temp/terraform.tfvars /home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars', shell = True)

    elif operating_system == "Windows":
  
        subprocess.call('cp /home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars /home/bala/Desktop/temp', shell = True)
        
        with open('./windows/terraform/terraform.tfvars'.format(config),'r') as file:
            tfvars_file = file.read()
                
        with open('./windows/terraform/terraform.tfvars', 'w+') as f_out:
            f_out.write(tfvars_file.format(**tfvars_config))
        
        os.chdir("./windows/terraform")
        subprocess.call('terraform init && terraform plan -out plan&& terraform apply "plan"', shell = True)
        shutil.copyfile('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraformLastState.tfvars')
        os.chdir(old_cwd)
        
        subprocess.call('cp /home/bala/Desktop/temp/terraform.tfvars /home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars', shell = True)

    subprocess.call('rm -rf /home/bala/Desktop/temp', shell = True)


def install_toolset(config):
    print("Wait until the success message is shown")
    operating_system = config['vm-info']['operating-system']
    if operating_system == "Linux":
        cmd = "ansible-playbook -i linux/ansible/hosts linux/ansible/playbook.yml --extra-vars=\'{\"tools\":" + str(config['vm-info']['toolset']) + "}\'" 
        os.system(cmd)
        
    elif operating_system == "Windows":
        # install 7zip
        cmd = "ansible-playbook -i windows/ansible/hosts windows/ansible/playbooks/install_7zip.yml"
        os.system(cmd)

        #install the chosen Toolset
        for tool in config['vm-info']['toolset']:
            cmd = "ansible-playbook -i windows/ansible/hosts windows/ansible/playbooks/" + playbooks_map[tool]
            os.system(cmd)

    print("Tool installation is complete")


def checkResources(args):

    totalVmCountInFile = 0
    for arg in args.config:        
        with open(arg, 'r') as f_config:
            config = json.load(f_config)
            if(config['vm-info']['operating-system'] != "Windows" and config['vm-info']['operating-system'] != "Linux"):
                print("Wrong operating-system in file " + str(arg) + ". It must be \"Windows\" or \"Linux\"")
                exit()
            if int(config['vm-info']['vm-ram']) > TOTAL_RAM_ALLOWED_ON_A_SINGLE_VM:
                print("You entered too much RAM memory. Exiting...")
                exit()
            totalVmCountInFile += int(config['vm-info']['vm-count'])
    if totalVmCountInFile > TOTAL_VMS_ALLOWED:
        print("You entered too many vm's. There is no enough space. Exiting...")
        exit()
    

def deleteInfrastrcture():
    if sys.argv[2] != "Linux" and sys.argv[2] != "Windows":
        print("You can only use \"Linux\" or \"Windows\"")
        exit()
    old_cwd = os.getcwd()
    if sys.argv[2] == "Linux":
        os.chdir("./linux/terraform")  
        shutil.copyfile('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars','/home/bala/Desktop/terraform.tfvars')
        os.remove('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')
        os.rename('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraformLastState.tfvars','/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')

        subprocess.call('terraform destroy --auto-approve', shell = True)
        
        os.rename('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraformLastState.tfvars')
        shutil.copyfile('/home/bala/Desktop/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')
        os.remove('/home/bala/Desktop/terraform.tfvars')
        
    if sys.argv[2] == "Windows":
        os.chdir("./windows/terraform")   
        shutil.copyfile('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars','/home/bala/Desktop/terraform.tfvars')
        os.remove('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')
        os.rename('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraformLastState.tfvars','/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')

        subprocess.call('terraform destroy --auto-approve', shell = True)
        
        os.rename('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraformLastState.tfvars')
        shutil.copyfile('/home/bala/Desktop/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')
        os.remove('/home/bala/Desktop/terraform.tfvars')  
    
    os.chdir(old_cwd)

def get_vim_objects(content, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vim_type], recursive=True).view]

def getTemplatesFromVCenter(listOfTemplates,config):
    si = connect.SmartConnect(host=config['vsphere-info']['vsphere-vcenter'], user=config['vsphere-info']['vsphere-user'], pwd=config['vsphere-info']['vsphere-password'], port=443)
    content = si.RetrieveContent()
    for vm in get_vim_objects(content, vim.VirtualMachine):
        if vm.config.template: 
            listOfTemplates.append(vm.name)
    return listOfTemplates


def checkTemplate(config,arg):
    template = config['vm-info']['vm-template-name']
    listOfTemplates = []
    listOfTemplates = getTemplatesFromVCenter(listOfTemplates,config)
    if template in listOfTemplates:
        print("Template name is correct...the deployment will start soon")
        return 0
    else:
        print("You have entered a template which does not exist in vCenter.")
        print("Do you want to deploy an infrastructure using an existing template? 1 - yes or 2 - no")
        choice = int(input())
        if choice == 1:
            if len(listOfTemplates) == 0:
                print("There are no templates existing in vCenter")
                print("Contact the administrator to build some templates...")
                exit()
            print("The available templates in vCenter are:")
            for i, template in enumerate(listOfTemplates):
                print(i+1,template)
            print("Enter the index of the template you want to make a deployment from")
            templateChoiceNumber = int(input())
            if templateChoiceNumber > len(listOfTemplates) or templateChoiceNumber == 0:
                print("You entered a wrong number...exiting")
                exit()
            templateChoiceName = listOfTemplates[templateChoiceNumber - 1]
            #schimba in fisier            
            with open(arg, "r") as jsonFile:
                data = json.load(jsonFile)            

            data["vm-info"]["vm-template-name"] = templateChoiceName
            if templateChoiceName == "Win2016-Template":
                data["vm-info"]["operating-system"] = "Windows"
            if templateChoiceName == "Ubuntu-1604-Template":
                data["vm-info"]["operating-system"] = "Linux"

            with open(arg, "w") as jsonFile:
                json.dump(data, jsonFile)    
            
            print("The deployment will start soon...")
            return 1
          

        else:
            print("Exiting...")
            exit()

        
def generate_ansible_host_file(config):
    if len(config['vm-info']['toolset']) == 0:
        print("No tools need to be installed")
        exit()

    operating_system = config['vm-info']['operating-system']

    ips=[]
    for i in range(int(config['vm-info']['vm-count'])):
        ips.append(str(config['network-info']['vm-ipv4-root']) + str(int(int(config['network-info']['vm-ipv4-start']) + int(i))))
    
    if operating_system == "Linux":
        #evita eroarea cu main in the middle vechile chei
        for ip in ips:
            command="ssh-keygen -f \"/home/bala/.ssh/known_hosts\" -R " + str(ip)
            os.system(command)

        with open('./templates/hosts_linux'.format(config), 'r') as f_in:
            hosts = f_in.read()
        info = {
            'linux-vms': '\n'.join(ips)
        }

        with open('./linux/ansible/hosts'.format(config), 'w+') as f_out:
            f_out.write(hosts.format(**info))
    if operating_system == "Windows":
        with open('./templates/hosts_windows'.format(config), 'r') as f_in:
            hosts = f_in.read()
            
        info = {
            'win-vms': '\n'.join(ips)
        }

        with open('./windows/ansible/hosts'.format(config), 'w+') as f_out:
            f_out.write(hosts.format(**info))

if __name__ == '__main__':
    parser = ArgumentParser(description = 'This module is used to automatically deploy a Windows/Linux infrastructure')
    parser.add_argument('-c', '--config', nargs='+', help = 'Path to configuration file', required = False)
    parser.add_argument('-d', '--delete', nargs='+', help = 'Linux or Windows infrastructure to be deleted', required = False)
    args = parser.parse_args()

    if not len(sys.argv) > 1:
        print("The script must be called with arguments")
        print("Use -c <config_file.json> for deploying an infrastructure")
        print("Use -d <Linux/Windows> for deleting the last infrastructure created with Linux or Windows")
        exit()
    
    if sys.argv[1] == "-d" or sys.argv[1] == "--delete":
        deleteInfrastrcture()
        exit()
  
    checkResources(args)

    for arg in args.config:        
        with open(arg, 'r') as f_config:
            config = json.load(f_config)
        changed = checkTemplate(config,arg)    
        if changed == 1:  
            with open(arg, 'r') as f_config:
                config = json.load(f_config)        
        generate_terraform_artefacts(config,{**config['vsphere-info'], **config['network-info'], **config['vm-info']})
        generate_ansible_host_file(config)
        install_toolset(config)

    print("Done..")
    
