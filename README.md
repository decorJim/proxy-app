key-pair

- change permission to read only enter command "sudo chmod 400 keyname.pem"
- verify ssh connection to master with command "sudo ssh -i keyname.pem -v root@masterip"

- change back permission for deletion command "sudo chmod 600 keyname.pem"

key installation

- Create a key called tmp1.pem and drop it in repo repo gatekeeper and trusted-host
- if repo gatekeeper or trusted-host already has it then copy and drop it in the current repo



