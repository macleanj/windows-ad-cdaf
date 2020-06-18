# Overview
Local Microsoft Active Directory setup for testing. The environment is extended from ["Continuous Delivery Automation Framework for Windows"](https://github.com/cdaf/windows). It seems not to be possible connect the local Active Directory to th AWS AD Connectory due to unstable socat port forwarders. This on its turn breaks the DNS queries to connect properly via TCP (for queries larger then 512 bits).

The VM is used for:
- PowerShell testing
- AD integration to cloud providers

General information:
- Default domain: ```mshome.net```
- Default credentials: ```vagrant/vagrant```
- ApacheDirectoryStudio```MSHOME\vagrant```. See password above.
- Domain/Forrest functional level: Windows Server 2016

Sources:
- [Setup on-prem AD with AWS](https://aws.amazon.com/premiumsupport/knowledge-center/enable-active-directory-console-access/)

# Setup
## VM
The following steps are needed to prepare the VM to enable management with pywinrm (from the MAC):
- Run ```vagrant up```
- Login -> Machine | Show
- Install Guest Additions -> Devices | Insert Guest Additions CD Image
- Enable Copy/Paste -> Devices | Shared Clipboard | Bidirectional
- Run PowerShell as Administrator
```
# winrm set winrm/config/service/auth '@{Basic="true"}'
# winrm set winrm/config/service @{AllowUnencrypted="true"}
```
- Turn off Firewall for Domain, Private, and Guest
> Checkpoint: now the system can be managed with pywinrm.

## Users and Groups
```
cd powershell
./prep_server.py
```
> STDERR gives some output, but this can be ignored.
> GUI verification: Active Directory Users and Computers | mshome.net | Users

| User | Password | Group | Scope |
| --- | --- | --- | --- |
| vagrant | default | admins | Global |
| ADConnectorService | see pw file | Connectors | Global |
| ad-readonly | see pw file | Cloud-ReadOnlyGroup | Global |
| ad-s3-user1 | see pw file | Cloud-S3-CrossLogic-AD1 | Global |
| ad-s3-user2 | see pw file | Cloud-S3-CrossLogic-AD2 | Global |

### Delegate privileges to your service account 
In the Active Directory User and Computers navigation tree, select your domain root. In the menu, select Action, and then Delegate Control.
- Select group "Connectors"
- Create a custom task to delegate
- Only the following objects in the folder (incl Create and Delete ticked):
  - account objects
  - Computer objects
  - User objects
- Add General and Property Specific: Read (and Write for Seamless Domain Join)



# Change domain name and controller
Optional <br>
[Documentation](http://www.rebeladmin.com/2015/05/step-by-step-guide-to-rename-active-directory-domain-name/)

**Add DNS Zone** <br>
- Primary Zone
- To all servers running on domain controller in this domain
- lab.crosslogic-consulting.com
- Allow only secure dynamic updates (default)

**Change domain name** <br>
In cmd (as admin):
- cd \vagrant\DirectoryServicePortTest
- rendom /list
- Change domain in file (DNSname: lab.crosslogic-consulting.com, NetBiosName: CROSSLOGIC)
- rendom /upload
- rendom /prepare (old domain is responding the success)
- rendom /execute (old domain is responding the success - DC is shutting down)
- ...System restarts...
> You need to login as user CROSSLOGIC/vagrant (once)

**Change domain controller name** <br>
In cmd (as admin):
- netdom computername dc.mshome.net /add:dc.lab.crosslogic-consulting.com
- netdom computername dc.mshome.net /makeprimary:dc.lab.crosslogic-consulting.com
- net config server /srvcomment:"lab.crosslogic-consulting.com Domain Controller"
- ...Reboot...

**Change domain controller policies** <br>
In cmd (as admin):
- gpfixup /olddns:mshome.net /newdns:lab.crosslogic-consulting.com
- gpfixup /oldnb:MSHOME /newnb:CROSSLOGIC
- rendom /end
- ...Reboot...

# Connecting the local vagrant Active Directory
The following section describes how to connect an on-prem Active Directory controller to an AWS AD Connector.

Discontinued:
- Client VPN connection cannot route back onto the VPN endpoint
- AD Connector does not route via public internet
- Unstable the socat port forwarders with SSH tunnel

**Software** <br>
Installed software on the vagrant Domain Controller:
- OpenVPN 64-bit
- Putty 64-bit

What should be copied in this directory from Service/System.....:
- EC2 credentials: aws-instances-ec2-user-custom-rsa,pem
- VPN credentials (.crt and .key)
- ovpn profile (after re-download from AWS)
- putty profile for tunnel

**ovpn profile** <br>
After downloading the ovnp from the Client VPN Endpoint, the ovpn file should end with:
```
cert C:\\vagrant\\aws.vpn\\vpn-client.lab.crosslogic-consulting.com.crt
key C:\\vagrant\\aws.vpn\\vpn-client.lab.crosslogic-consulting.com.key
```

The ovpn file needs to be updated to the OpenVPN/config dir.

**putty profile for tunnel**
import private ssh key into puttygen and save it as a ppk key.

**EC2 SSH Tunnel**
change /etc/ssh/sshd_config (not needed for Amazon linux):
- PermitTunnel yes``` 
- AllowTcpForwarding yes
- GatewayPorts clientspecified
- X11Forwarding yes
```
sudo service sshd restart
```

On on-prem system (first) <br>
```
# UDP and TCP forwarding
EC2Address=54.156.85.95
ssh -R localhost:5353:localhost:5353 -R localhost:1053:localhost:1053 \
    -R localhost:8888:localhost:8888 -R localhost:1088:localhost:1088 \
    -R localhost:3838:localhost:3838 -R localhost:1389:localhost:1389 \
    ec2-user@$EC2Address
# Mapping UDP
sudo socat tcp4-listen:5353,fork UDP:localhost:1053 &
sudo socat tcp4-listen:8888,fork UDP:localhost:1088 &
sudo socat tcp4-listen:3838,fork UDP:localhost:1389 &
# sudo pkill socat
```

On EC2 (second) <br>
```
# Install dependencies
sudo yum update
sudo yum install socat

# Mapping UDP
sudo socat udp4-listen:53,fork tcp:localhost:5353 &
sudo socat udp4-listen:88,fork tcp:localhost:8888 &
sudo socat udp4-listen:389,fork tcp:localhost:3838 &
# Mapping TCP privileged to TCP non-privileged 
sudo socat tcp4-listen:53,fork tcp:localhost:1053 &
sudo socat tcp4-listen:88,fork tcp:localhost:1088 &
sudo socat tcp4-listen:389,fork tcp:localhost:1389 &
# sudo pkill socat
```

Test <br>
To test from local Windows VM, temporily change Security Group to full inbound access (testing only!!). Make sure VPN is working towards the internet to be able to use the public IP address.
```
nslookup -port=53 dc.mshome.net 54.156.85.95 # UDP
nslookup "-set vc" -port=53 dc.mshome.net 54.156.85.95 # TCP
nslookup -port=53 _ldap._tcp.mshome.net 54.156.85.95
nslookup -port=53 _kerberos._tcp.mshome.net 54.156.85.95
.\DirectoryServicePortTest.exe -d mshome.net -ip 54.156.85.95 -tcp "53,88,389" -udp "53,88,389"

nslookup -port=53 dc.mshome.net 91.195.92.26
nslookup -port=53 _ldap._tcp.mshome.net 91.195.92.26
nslookup -port=53 _kerberos._tcp.mshome.net 91.195.92.26
.\DirectoryServicePortTest.exe -d mshome.net -ip 91.195.92.26 -tcp "53,88,389" -udp "53,88,389"
```




# AWS
## AD Connector
Setup AWS AD Connector to an existing AD (this one):
- Directory Service | Directories | Set up a directory
- Select 2 public subnets (1a, 1b) from the shared VPN
- Directory name: mshome.net
- DNS IP: 91.195.92.26 (on-prem)
- vagrant / vagrant

Troubleshooting:
- [AWS documentation](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_troubleshooting.html)
- From AWS: nslookup  _ldap._tcp.mshome.net [public ip address]
- Download and test [DirectoryServicePortTest.exe](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/samples/DirectoryServicePortTest.zip). Downgrade temporarily the Domain/Forrest functional level: 
  - ```Set-ADForestMode -Identity "mshome.net" -ForestMode "Windows2012R2Forest"```
  - ```Set-ADDomainMode –Identity "mshome.net" –DomainMode "Windows2012R2Domain"```

