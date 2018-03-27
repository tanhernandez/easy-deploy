from tkinter import ttk
import tkinter as tk
import paramiko
import settings


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # Define ENV Properties
        self.DEV_BRANCH = settings.DEV_BRANCH
        self.PROD_BRANCH = settings.PROD_BRANCH
        self.DEV_IP = settings.DEV_IP
        self.PROD_IP = settings.PROD_IP
        self.PUBLIC_SSH_KEY = settings.PUBLIC_SSH_KEY

        # Define SELF Properties
        self.dev_branch_name = tk.StringVar()
        self.prod_branch_name = tk.StringVar()
        self.need_checkout_branch = tk.IntVar()
        self.need_npm_install = tk.IntVar()
        self.need_npm_update = tk.IntVar()
        self.need_npm_prod = tk.IntVar()
        self.do_deploy_to_prod = tk.IntVar()

        self.set_default_props()

        # Start create widget parts ---
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def set_default_props(self):
        self.dev_branch_name.set(self.DEV_BRANCH)
        self.prod_branch_name.set(self.PROD_BRANCH)
        self.need_checkout_branch.set(0)
        self.need_npm_install.set(0)
        self.need_npm_update.set(0)
        self.need_npm_prod.set(0)
        self.do_deploy_to_prod.set(0)

    def create_spacer(self, pad):
        ttk.Frame(self, relief='flat', borderwidth=1).pack(pady=pad)

    def create_label(self, content):
        ttk.Label(self, text=content).pack(pady=5)

    def create_text_field(self, vbind):
        ttk.Entry(self, textvariable=vbind).pack(pady=5)

    def create_checkbox(self, vbind, lbl=''):
        ttk.Checkbutton(self, text=lbl, onvalue=1, offvalue=0, variable=vbind).pack(pady=5)

    def create_button(self, title, callback):
        ttk.Button(self, text='  ' + title + '  ', command=callback).pack(pady=5)

    def create_widgets(self):
        # Create field for Development Branch
        self.create_label('Development Branch')
        self.create_text_field(self.dev_branch_name)
        self.create_spacer(5)

        # Create field for Production Branch
        self.create_label('Production Branch')
        self.create_text_field(self.prod_branch_name)

        self.create_spacer(10)

        # Create checkbox to know if check out branch is needed
        self.create_checkbox(self.need_checkout_branch, 'Do checkout to branch?')

        # Create checkbox to know if NPM install is needed
        self.create_checkbox(self.need_npm_install, 'Do NPM Install?')

        # Create checkbox to know if NPM update is needed
        self.create_checkbox(self.need_npm_update, 'Do NPM Update?')

        # Create checkbox to know if which to use between NPM dev or NPM prod
        self.create_checkbox(self.need_npm_prod, 'Do NPM Prod?')

        # Create checkbox enable/disable the DEPLOY TO PROD button for safety purposes
        self.create_checkbox(self.do_deploy_to_prod, 'Enable Deploy to Prod?')

        # Create the Buttons
        self.create_spacer(10)
        self.create_button('Deploy Now', self.deploy_now)
        self.create_button('Default', self.set_default_props)
        self.create_button('Close', root.destroy)

    @staticmethod
    def print_y_or_n(content, v):
        r = 'No'
        if v:
            r = 'Yes'
        print(content, r)

    def gather_values(self):
        print('----------------------------------------')
        print('Printing out defined values...')
        print('----------------------------------------')
        print('Development Branch Name:', self.dev_branch_name.get())
        print('Production Branch Name:', self.prod_branch_name.get())
        self.print_y_or_n('Is checkout to branch needed?', self.need_checkout_branch.get())
        self.print_y_or_n('Is npm install needed?', self.need_npm_install.get())
        self.print_y_or_n('Is npm update needed?', self.need_npm_update.get())
        self.print_y_or_n('Is npm prod needed?', self.need_npm_prod.get())
        self.print_y_or_n('Are we deploying to PRODUCTION Server?', self.do_deploy_to_prod.get())

    def prepare_commands(self, branch, path):

        # Track and print the values defined
        self.gather_values()
        print('\nPreparing command set...')

        # Navigate into the given path
        command_set = [f'cd {path}']

        # If needed, do checkout to branch
        if self.need_checkout_branch.get():
            command_set.append(f'git checkout {branch}')

        # Initiate git pull
        command_set.append(f'git pull origin {branch}')

        # If needed, do npm install
        if self.need_npm_install.get():
            command_set.append('npm install')

        # If needed, do npm update
        if self.need_npm_update.get():
            command_set.append('npm update')

        # If needed, do npm prod else do npm dev
        if self.need_npm_prod.get():
            command_set.append('npm run prod')
        else:
            command_set.append('npm run dev')

        verbiage_commands = ''
        for index, item in enumerate(command_set):
            if index == 0:
                verbiage_commands += item
            else:
                verbiage_commands += '\n' + item

        print('----------------------------------------')
        print(verbiage_commands)
        print('----------------------------------------')

        return verbiage_commands

    def deploy_to_dev(self):
        # Prepare commands
        path = '/var/www/wc'
        branch = self.dev_branch_name.get()
        commands = self.prepare_commands(branch, path)
        # Connect to HOST
        host = self.DEV_IP
        self.connect_via_ssh(host, commands)

    def deploy_to_prod(self):
        # Prepare commands
        path = '/var/www/html/wc'
        branch = self.prod_branch_name.get()
        commands = self.prepare_commands(branch, path)
        # Connect to HOST
        # hosts = [x.strip() for x in self.PROD_IP.split(',')]
        # for host in hosts:
        #     self.connect_via_ssh(host, commands)

    def deploy_now(self):
        if self.do_deploy_to_prod.get():
            print('Deploying to Production Server...\n')
            self.deploy_to_prod()
        else:
            print('Deploying to Development Server...\n')
            self.deploy_to_dev()

    @staticmethod
    def connect_via_ssh(host, commands):

        ssh_client = None
        try:
            # Split the IP from the username
            cred = host.split('@')

            # Initiate SSH Connection
            print('\n\nConnecting via SSH to ' + host + ' ...')
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
            ssh_client.connect(cred[1], port=22, username=cred[0])
            stdin, stdout, stderr = ssh_client.exec_command(commands)
            stdout.channel.recv_exit_status()
            for line in stdout.readlines():
                print(line)

        finally:
            ssh_client.close()
            print('SSH Session Ended Successfully')


root = tk.Tk()
root.title('Easy Deploy')
root.geometry('300x520')
app = App(master=root)
app.mainloop()
