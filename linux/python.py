import subprocess
import os
import re

LINUX_ANSIBLE_HOSTS_FILE = "ansible/hosts"
LINUX_TERRAFORM_VAR_FILE = "terraform/variables.tf"

print("Doriti sa lansati in executie masini de Linux?")
a = 0
a = input()
a = int(a)

if a == 1:
    
    # creez masini de linux
    # verific daca template ul exista
    # checkTemplate.sh

    #exista
    print("Cate masini de linux doriti?")
    nrmasinilinux = 0
    nrmasinilinux = input()
    
    
    print("Wait until complete message")
    
    old_cwd = os.getcwd()
    os.chdir("terraform")
    subprocess.call(["../scriptterraform.sh",nrmasinilinux])
    os.chdir(old_cwd)
    
    print("The installation is complete")

    # creating an empty list
    lst = []

    # number of elements as input
    n = int(input("Introduce the number of software tools you want to install on the VMs : "))

    #making hosts file
    #ips = []
    filename = open(LINUX_TERRAFORM_VAR_FILE,"r")
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
    
    f_out = open(LINUX_ANSIBLE_HOSTS_FILE,"w")
    f_out.write("[linuxvms]\n")
    after = " ansible_user=kopicloud ansible_password=kopicloud\n"
    for i in range(int(nrmasinilinux)):
        f_out.write(str(ipv4_root) + str(int(int(ipv4_start) + int(i))) + after)
    f_out.close()


    # iterating till the range
    for i in range(0, n):
        ele = (input())
        lst.append(ele) # adding the element

    my_products = ('["' + '","'.join(lst) + '"]')

    print("Wait until the success message is shown")

    cmd = "ansible-playbook -i ansible/hosts ansible/playbook.yml --extra-vars=\'{\"tools\":" + my_products + "}\'"

    os.system(cmd)

    print("Tool installation is complete")
    print("Now the VMs are created and the toolset is already installed on them")

