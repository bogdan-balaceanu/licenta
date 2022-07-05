import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from pyVmomi import vim
from pyVim import connect
from os import listdir
from os.path import isfile, join
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

PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY = "/home/bala/Desktop/repo_licenta/licenta/infrastructures_created"

TOTAL_VMS_ALLOWED = 20
TOTAL_RAM_ALLOWED_ON_A_SINGLE_VM = 4096

LINUX_ANSIBLE_HOSTS_FILE = "./linux/ansible/hosts"
WINDOWS_ANSIBLE_HOSTS_FILE = "./windows/ansible/hosts"

def checkExistenceOfInfrastructureDirectory():
    isDir = os.path.isdir(PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY) 
    if isDir == False:
        os.mkdir(PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY)
def checkNameOfInfrastructure(nameOfTfvarsFile):
    tfvarsFiles = [f for f in listdir(PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY) if isfile(join(PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY, f))]
    for tfvarsFile in tfvarsFiles:
        if nameOfTfvarsFile == tfvarsFile:
            return 1
            
    return 0

def checkTfState(operating_system):
    path = "/home/bala/Desktop/repo_licenta/licenta" + "/" + operating_system + "/terraform"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    os.chdir(path)
    for f in files:
        if f == "terraform.tfstate" or f == "terraform.tfstate.backup":
            os.remove(f)

def generate_terraform_artefacts(config,tfvars_config):
    
    checkExistenceOfInfrastructureDirectory()
    nameOfTfvarsFile = config['unique-id'] + ".tfvars"
    if checkNameOfInfrastructure(nameOfTfvarsFile) == 1:
        print("There is already an infrastructure with the name " + nameOfTfvarsFile + " in the infrastructure_created directory. Please modify the unique-id in config file.")
        exit()
    
    destinationName = PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY + "/" + config['unique-id'] + ".tfvars"
    destinationNameForTfstate=PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY + "/" + config['unique-id'] + ".tfstate"
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
        checkTfState("linux")

        subprocess.call('terraform init && terraform plan -out plan && terraform apply "plan"', shell = True)
        
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars',destinationName)
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfstate',destinationNameForTfstate)

        os.chdir(old_cwd)

        subprocess.call('cp /home/bala/Desktop/temp/terraform.tfvars /home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars', shell = True)

    elif operating_system == "Windows":
  
        subprocess.call('cp /home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars /home/bala/Desktop/temp', shell = True)
        
        with open('./windows/terraform/terraform.tfvars'.format(config),'r') as file:
            tfvars_file = file.read()
                
        with open('./windows/terraform/terraform.tfvars', 'w+') as f_out:
            f_out.write(tfvars_file.format(**tfvars_config))
        
        os.chdir("./windows/terraform")
        checkTfState("windows")

        subprocess.call('terraform init && terraform plan -out plan && terraform apply "plan"', shell = True)
        
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars',destinationName)
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfstate',destinationNameForTfstate)

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

def getListOfIpInVCenter(listofIpInVCenter,config):
    si = connect.SmartConnect(host=config['vsphere-info']['vsphere-vcenter'], user=config['vsphere-info']['vsphere-user'], pwd=config['vsphere-info']['vsphere-password'], port=443)
    content = si.RetrieveContent()
    for vm in get_vim_objects(content, vim.VirtualMachine):
        if vm.config: 
            listofIpInVCenter.append(vm.guest.ipAddress) 
    return listofIpInVCenter

def checkIpRange(config):
    ipStart = config['network-info']['vm-ipv4-root'] + config['network-info']['vm-ipv4-start']
    count = config['vm-info']['vm-count']
    listofIpInVCenter = []
    listofIpInVCenter = getListOfIpInVCenter(listofIpInVCenter,config)
    listofIpInConfigFile = []
    for i in range(int(count)):
        lastNumb = int(config['network-info']['vm-ipv4-start']) + int(i)   
        ip = config['network-info']['vm-ipv4-root'] + str(lastNumb)
        listofIpInConfigFile.append(ip)
    
    for ipInConfigFile in listofIpInConfigFile:
        for ipInVCenter in listofIpInVCenter:
            if ipInConfigFile == ipInVCenter:
                print(ipInConfigFile + " is already used in vCenter, please reconfigure the network settings in config file.")
                exit()
        

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
            checkIpRange(config)
    if totalVmCountInFile > TOTAL_VMS_ALLOWED:
        print("You entered too many vm's. There is no enough space. Exiting...")
        exit()
    

def deleteInfrastrcture():
    infrastructureName = sys.argv[2] + ".tfvars"
    infratructureNameStatev = sys.argv[2] + ".tfstate"
    if checkNameOfInfrastructure(infrastructureName) == 0 or checkNameOfInfrastructure(infratructureNameStatev) == 0:
        print("There is no file called " + infrastructureName + " or " + infratructureNameStatev + " in the infrastructure_created directory.")
        exit()

    #ii fac load
    pathForTfvars = PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY + "/" + infrastructureName
    pathForTfstate = PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY + "/" + infratructureNameStatev
    #ii iau sistemul de operare
    #os.chdir(PATH_TO_INFRASTRUCTURE_HISTORY_DIRECTORY)
    with open(pathForTfstate, 'r') as f_config:
        config = json.load(f_config)
    if config['resources'][4]['instances'][0]['attributes']['name'] == "Ubuntu-1604-Template":
        operating_system = "Linux"
    else:
        if config['resources'][4]['instances'][0]['attributes']['name'] == "Win2016-Template":
            operating_system = "Windows"
        else:
            print("The name of template in vCenter are different from the existing one tfstate file. The destruction cannot be completed...")
            exit()

    #ii iau sistemul de operare
    if operating_system == "Linux":
        # iau sablonul cu cut pe desktop
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars','/home/bala/Desktop/terraform.tfvars')
        # iau fisierele si le duc in terraform
        shutil.move(pathForTfvars,'/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')
        shutil.move(pathForTfstate,'/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfstate')
        os.chdir('/home/bala/Desktop/repo_licenta/licenta/linux/terraform')
        subprocess.call('terraform destroy --auto-approve', shell = True)
        #sterg ala folosit din terrafrom
        os.remove('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')
        os.remove('/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfstate')
        #duc inapoi sablonul de pe desktop
        shutil.move('/home/bala/Desktop/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/linux/terraform/terraform.tfvars')

    if operating_system == "Windows":
        # iau sablonul cu cut pe desktop
        shutil.move('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars','/home/bala/Desktop/terraform.tfvars')
        # iau fisierele si le duc in terraform
        shutil.move(pathForTfvars,'/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')
        shutil.move(pathForTfstate,'/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfstate')
        os.chdir('/home/bala/Desktop/repo_licenta/licenta/windows/terraform')
        subprocess.call('terraform destroy --auto-approve', shell = True)
        #sterg ala folosit din terrafrom
        os.remove('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')
        os.remove('/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfstate')
        #duc inapoi sablonul de pe desktop
        shutil.move('/home/bala/Desktop/terraform.tfvars','/home/bala/Desktop/repo_licenta/licenta/windows/terraform/terraform.tfvars')


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
        print("You entered more than 1 config file. You must be aware of network mistakes. Do you want to continue? 1 - Yes or 2 - NO")
        choice = input()
        if choice.isdigit() != 1:
            print("You entered something different a number...exiting")
            exit()
        if int(choice) == 1:
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
        return()

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
    install_toolset(config)

def getInformationAboutVMs(config):
    si = connect.SmartConnect(host=config['vsphere-info']['vsphere-vcenter'], user=config['vsphere-info']['vsphere-user'], pwd=config['vsphere-info']['vsphere-password'], port=443)
    content = si.RetrieveContent()
    for vm in get_vim_objects(content, vim.VirtualMachine):
        if vm.config:
            if str(vm.guest.ipAddress) == "None":
                print(("Could not get the IP address of VM with name ") + str(vm.name) + " because is shutted down. Power on the VM to get its IP.")
            else:
                print(("VM with name ") + str(vm.name) + (" has the following IP address: ") + str(vm.guest.ipAddress))


if __name__=='__main__':
    parser = ArgumentParser(description = 'This module is used to automatically deploy a Windows/Linux infrastructure')
    parser.add_argument('-c', '--config', nargs='+', help = 'Path to configuration file', required = False)
    parser.add_argument('-d', '--delete', nargs='+', help = 'Linux or Windows infrastructure to be deleted', required = False)
    parser.add_argument('-i', '--info', nargs='+', help = 'Information about existing virtual machines in vCenter', required = False)
    args = parser.parse_args()

    if not len(sys.argv) > 1:
        print("The script must be called with arguments")
        print("Use -c <config_file.json> for deploying an infrastructure")
        print("Use -d <unique-id> for deleting the infrastructure with that id")
        print("Use -i <config_file.json> for obtaining information about existing virtual machines in vCenter")
        exit()

    if sys.argv[1] == "-d" or sys.argv[1] == "--delete":
        deleteInfrastrcture()
        exit()

    if sys.argv[1] == "-i" or sys.argv[1] == "--info":
        with open(sys.argv[2], 'r') as f_config:
            config = json.load(f_config)
        getInformationAboutVMs(config)
        exit()
    
    

    if len(sys.argv) - 2 >= 2:
        print("You entered more than 1 config file. You must be aware of network mistakes. Do you want to continue? 1 - Yes or 2 - NO")
        choice = input()
        if choice.isdigit() != 1:
            print("You entered something different from 1 or 2...exiting")
            exit()
        if int(choice) == 2:
            exit()

    checkResources(args)    

    for arg in args.config:   
        with open(arg, 'r') as f_config:
            config = json.load(f_config)
        checkTemplate(config,arg)     
        generate_terraform_artefacts(config,{**config['vsphere-info'], **config['network-info'], **config['vm-info']})
        generate_ansible_host_file(config)
        

    print("Done..")