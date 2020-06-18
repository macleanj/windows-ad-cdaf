from winrm import Protocol
import base64
import sys
address = "127.0.0.1"
transport = "plaintext"
username = "vagrant"
password = "vagrant"
protocol = "http"
port = 55985

endpoint = "%s://%s:%s/wsman" % (protocol, address, port)

conn = Protocol(endpoint=endpoint, transport=transport,
                username=username, password=password)
shell_id = conn.open_shell()


# the text file we want to send
# this could be populated by reading a file from disk instead
# has some special characters, just to prove they won't be a problem
text_file = """this is a multiline file
that contains special characters such as
"blah"
'#@$*&&($}
that will be written
onto the windows box"""

# first part of the powershell script
# streamwriter is the fastest and most efficient way to write a file
# I have found
# notice the @", this is like a "here document" in linux
# or like triple quotes in python and allows for multiline files
# the file will be placed in the home dir of the user that 
# logs into winrm (administrator in this case)
part_1 = """$stream = [System.IO.StreamWriter] "test.txt"
$s = @"
"""

# second part of the powershell script
# the "@ closes the string
# the replace will change the linux line feed to the
# windows carriage return, line feed
part_2 = """
"@ | %{ $_.Replace("`n","`r`n") }
$stream.WriteLine($s)
$stream.close()"""

# join the beginning of the powershell script with the
# text file and end of the ps script
script = part_1 + text_file + part_2

# base64 encode, utf16 little endian. required for windows
encoded_script = base64.b64encode(script.encode("utf_16_le"))

# send the script to powershell, tell it the script is encoded
command_id = conn.run_command(shell_id, "powershell -encodedcommand %s" %
                            (encoded_script))
stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
conn.cleanup_command(shell_id, command_id)
print("STDOUT: %s"%(stdout.decode("utf-8")))
print("STDERR: %s"%(stderr.decode("utf-8")))

# print the file
command_id = conn.run_command(shell_id, "type test.txt")
stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
conn.cleanup_command(shell_id, command_id)
print("STDOUT: %s"%(stdout.decode("utf-8")))
print("STDERR: %s"%(stderr.decode("utf-8")))

# delete the file
command_id = conn.run_command(shell_id, "del test.txt")
stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
conn.cleanup_command(shell_id, command_id)
print("STDOUT: %s"%(stdout.decode("utf-8")))
print("STDERR: %s"%(stderr.decode("utf-8")))

# always good to clean things up, doesn't hurt