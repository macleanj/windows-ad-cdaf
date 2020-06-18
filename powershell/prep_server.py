#!/usr/bin/env python3

import winrm

passwordFile = "password.txt"
with open(passwordFile, 'r') as file:
  userPassword = file.read()

psFile = "users_groups.ps1"
with open(psFile, 'r') as file:
  psScript = file.read().replace("__PASSWORD__", userPassword)

print("psScript: %s"%(psScript))

session = winrm.Session('127.0.0.1:55985', auth=('vagrant', 'vagrant'))
result = session.run_ps(psScript)
print("STATUS: %s"%(result.status_code))
print("STDOUT: %s"%(result.std_out.decode("utf-8")))
print("STDERR: %s"%(result.std_err.decode("utf-8")))
