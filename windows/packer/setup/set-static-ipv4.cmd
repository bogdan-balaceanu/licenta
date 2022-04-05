netsh interface ipv4 set address name="Ethernet0" static 10.230.30.107 255.255.255.0 10.230.30.1

netsh interface ipv4 set dns name="Ethernet0" source=static address=10.230.30.111 primary


netsh Advfirewall set allprofiles state off

Enable-PSRemoting -Force -SkipNetworkProfileCheck 
netsh advfirewall firewall add rule name="WinRM-HTTP" dir=in localport=5985 protocol=TCP action=allow
netsh advfirewall firewall add rule name="WinRM-HTTPS" dir=in localport=5986 protocol=TCP action=allow
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'



