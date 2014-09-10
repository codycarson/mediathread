# Ansible setup

1. Install ansible: `pip install ansible`
2. Clone the git repo: `git clone https://github.com/appsembler/mediathread.git`
3. Enter the deploy folder: `cd deploy`
4. Enter the IP address of the server under `[server]` in the inventory file under `hosts/<server_type>/inventory`
5. Copy the example settings file: `cp hosts/<server_type>/all.example hosts/<server_type>/all`
6. Fill the required values in the `hosts/<server_type>/all` file
7. Run the ansible scripts: `ansible-playbook -i hosts/<server_type>/inventory site.yml`
