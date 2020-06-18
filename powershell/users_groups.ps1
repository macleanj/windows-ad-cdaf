#location where makecert tool is present, you can find this tool part of Windows SDK
# $makecertpath = 'c:\temp\makecert.exe'
$domainname = "mshome.net"
# $netbiosname = "mshome.net"
#for illustration password is hardcoded, best is to use Get-Credential
$password = ConvertTo-SecureString "__PASSWORD__" -AsPlainText -Force

# Service Account for AD Connector. Needs to be extended with permissions
$connectorsUser = "ADConnectorService"
New-ADUser -Name $connectorsUser -AccountPassword $password -EmailAddress "$connectorsUser@$domainname" -Enabled $true
$connectorsGroup = "Connectors"
New-ADGroup $connectorsGroup -GroupScope Global -GroupCategory Security
Add-ADGroupMember -Identity $connectorsGroup -Members $connectorsUser


#Add users, that will used for SSO
$user = "ad-readonly"
New-ADUser -Name $user -AccountPassword $password -EmailAddress "$user@$domainname" -Enabled $true
$group = "Cloud-ReadOnlyGroup"
New-ADGroup $group -GroupScope Global -GroupCategory Security
Add-ADGroupMember -Identity $group -Members $user

$user = "ad-s3-user1"
New-ADUser -Name $user -AccountPassword $password -EmailAddress "$user@$domainname" -Enabled $true
$group = "Cloud-S3-CrossLogic-AD1"
New-ADGroup $group -GroupScope Global -GroupCategory Security
Add-ADGroupMember -Identity $group -Members $user

$user = "ad-s3-user2"
New-ADUser -Name $user -AccountPassword $password -EmailAddress "$user@$domainname" -Enabled $true
$group = "Cloud-S3-CrossLogic-AD2"
New-ADGroup $group -GroupScope Global -GroupCategory Security
Add-ADGroupMember -Identity $group -Members $user
