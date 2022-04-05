import subprocess
import os
import re

playbooks_map = {
    "vscode": "install_vscode.yml",
    "notepad++": "install_npp.yml",
    "dnspy": "install_dnspy.yml",
    "putty": "install_putty.yml",
    "winscp": "install_winscp.yml",
    "wireshark": "install_wireshark.yml"
}

WINDOWS_ANSIBLE_HOSTS_FILE = "ansible/hosts"
WINDOWS_TERRAFORM_VAR_FILE = "terraform/variables.tf"

print("Doriti sa lansati in executie masini de Windows?")
a = 0
a = input()
a = int(a)

if a == 1:
    print("Cate masini de windows doriti?")
    nrmasiniwindows = 0
    nrmasiniwindows = input()
    print("Wait until complete message")

    old_cwd = os.getcwd()
    os.chdir("terraform")
    subprocess.call(["../scriptterraformwin.sh",nrmasiniwindows])
    os.chdir(old_cwd)

    print("The installation is complete")

    #making hosts file
    #ips = []
    filename = open(WINDOWS_TERRAFORM_VAR_FILE,"r")
    lines = filename.readlines()
    flag = 0
    flag1 = 0 
    for line in lines:
        if(flag == 1):
            flag = 0
            ipv4_root = line.split('"')[1].split('"')[0]
 #           print(ipv4_root)
        if(flag1 == 1):
            flag1 = 0
            ipv4_start = line.split('"')[1].split('"')[0]
            #ipv4_start = ipv4_root + ipv4_start
#            print(ipv4_start)
            break
        if(line.find('ipv4_root') != -1):
             flag = 1
        if(line.find('ipv4_start') != -1):
             flag1 = 1
    
    f_out = open(WINDOWS_ANSIBLE_HOSTS_FILE,"w")
    f_out.write("[winhosts]\n")
    after = " ansible_user=Administrator ansible_password=S3cr3t! ansible_connection=winrm ansible_winrm_transport=basic ansible_winrm_server_cert_validation=ignore\n"
    for i in range(int(nrmasiniwindows)):
        f_out.write(str(ipv4_root) + str(int(int(ipv4_start) + int(i))) + after)
    f_out.close()

    print("Tool-uri disponibile: ")
    for k in playbooks_map:
        print(" - " + k)

    n = int(input("Introduce the number of software tools you want to install on the VMs : "))

    tools_list = []
    for i in range(1,n + 1):
        tool = str(input("Tool number " + str(i)  + " : "))
        tools_list.append(tool)

    print("Wait until the success message is shown")

    # install 7zip
    cmd = "ansible-playbook -i ansible/hosts ansible/playbooks/install_7zip.yml"
    os.system(cmd)

    for tool in tools_list:
        cmd = "ansible-playbook -i ansible/hosts ansible/playbooks/" + playbooks_map[tool]
        os.system(cmd)

    print("The toolset you chose has been successfully installed on the VMs.")
