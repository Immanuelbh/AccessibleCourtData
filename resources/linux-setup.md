# Set up on remote linux server
## Prerequisites
- Git
- Docker
- Python3
- Pip3

## Update Aptitude: `$ sudo apt-get update`

### Git
`$ sudo apt-get install git`

### Python3
`$ sudo apt install python3.9`

### Pip3
`$ sudo apt-get -y install python3-pip`

### Docker (from the official documentation)
Installing the repository
1. `sudo apt-get remove docker docker-engine docker.io containerd runc`
2. `sudo apt-get update`
3. `sudo apt-get install \
   apt-transport-https \
   ca-certificates \
   curl \
   gnupg \
   lsb-release`
4. `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg`
5. `echo \
   "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`

#### Installing Docker Engine
6. `sudo apt-get update`
7. `sudo apt-get install docker-ce docker-ce-cli containerd.io`

#### Test
8. `sudo docker run hello-world`

Finally, add privileges to users:
`sudo chmod 666 /var/run/docker.sock`