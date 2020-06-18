import winrm
import sys

session = winrm.Session('127.0.0.1:55985', auth=('vagrant', 'vagrant'))
result = session.run_cmd('ipconfig', ['/all'])

# Option 1
# print(result.std_out.decode("utf-8"))

# Option 2
# sys.stdout.write('STDOUT: {0}'.format(result.std_out.decode("utf-8")))
# sys.stdout.flush()

# Option 3
print("STDOUT: %s"%(result.std_out.decode("utf-8")))
