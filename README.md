key-pair

- change permission to read only enter command "sudo chmod 400 keyname.pem"
- verify ssh connection to master with command "sudo ssh -i keyname.pem -v root@masterip"

- change back permission for deletion command "sudo chmod 600 keyname.pem"



