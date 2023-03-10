import os
import sys

domain=""
email=""
postgres_password=""
#leave empty for standard ssh port (22)
ssh_port = ""
#provide your public ip adress - you can lookup at wieistmeineip.at
ip = ""
#want to create the homeserver key on yourself? answer with True or False
add_key=True
#if True insert your generated key here (generate it with pwgen -s 64 1)
homeserver_key=""

#bridges, set variable <true> if you want to install them or <false> e.g: mautrix-bridge=true
mautrix_discord_bridge=True
mautrix_signal_bridge=True
heisenberg_bridge=True
#write your username in matrix format e.g @your-username:domain
heisenbridge_owner=""

#if true fill out client id and token, you would get that from the discord developers dashboard when creating a bot
appservice_discord_bridge=True
appservice_discord_brige_client_id="" #
appservice_discord_bridge_token=""

#want to run your own nginx server? set the ports where matrix-nginx should run and reverse proxy it from your nginx
http_port=
https_port=

if ip is None:
    print("ERROR: IP variable empty")
    sys.exit()

if heisenberg_bridge == True and not heisenbridge_owner:
    print("please fill in a matrix user")
    sys.exit()

if appservice_discord_bridge and not appservice_discord_brige_client_id or not appservice_discord_bridge_token:
    print("ERROR: fill out all appservice variables")
    sys.exit()
#os.system("sudo dnf install pwgen -y")
def func(string):
    return ''.join(string.splitlines())


user=os.environ.get('USER')
key = os.environ.get('MATRIX_KEY')
print(key)
if key is None and add_key == False:
    homeserver_key=os.popen("pwgen -s 64 1").read()
    homeserver_key=func(homeserver_key)
    print("if ist durch")
    with open('/home/{}/.bashrc'.format(user), 'a') as f:
            f.write("export MATRIX_KEY={}".format(homeserver_key))
            f.close()
elif key is not None and add_key == False:
    homeserver_key = key
print(key)
file_path = os.path.dirname(os.path.realpath(__file__))
yml_path= "{}/inventory/host_vars/matrix.{}".format(file_path, domain)
hosts_path = "{}/inventory/".format(file_path)
try:
    if not os.path.exists(yml_path):
        os.makedirs(yml_path)
        #os.mkdir(yml_path)
        os.system("touch {}/vars.yml".format(yml_path))
        os.system("touch {}/hosts".format(hosts_path))
        with open('{}/hosts'.format(hosts_path), 'w') as f:
            hosts_write = [
                "[matrix_servers]\n",
                "matrix.{} ansible_host={} ansible_port={} ansible_ssh_user=root".format(domain, ip, ssh_port)
            ]
            f.writelines(hosts_write)
except OSError as e:
    print(e)

with open('{}/foo.yml'.format(yml_path), 'r+') as f:
    lines = [
        'matrix_domain: {}\n'.format(domain),
        'matrix_homeserver_implementation: synapse\n',
        "matrix_homeserver_generic_secret_key: '{}' \n".format(homeserver_key),
        'matrix_ssl_lets_encrypt_support_email: "{}" \n'.format(email),
        "devture_postgres_connection_password: '{}' \n".format(postgres_password),
        'matrix_well_known_matrix_support_enabled: true\n',
        'matrix_nginx_proxy_base_domain_serving_enabled: true\n'
    ]
    content = f.read()
    #if "matrix_homeserver_generic_secret_key:" not in content:
    #    lines[0] = "matrix_homeserver_generic_secret_key: '{}' \n".format(homeserver_key)
    for i, line in enumerate(lines):
        get_line = line.split(": ")[0].strip()
        get_var = line.split(": ")[1].strip()
        print(get_var)
        print(line)
        if get_line not in content:
            print("get_line wurde aufgerufen")
            lines[i] = "{}: {}\n".format(get_line, get_var)
        elif get_var not in content:
            print(i)
            lines[i] = "{}: {}\n".format(get_line, get_var)
    f.seek(0)
    f.truncate()
    f.writelines(lines)
    f.close()

if mautrix_discord_bridge:
    with open('{}/foo.yml'.format(yml_path), 'a') as f:
        f.write("matrix_mautrix_discord_enabled: true\n")
        f.close()
if mautrix_signal_bridge:
    with open('{}/foo.yml'.format(yml_path), 'a') as f:
        f.write("matrix_mautrix_signal_enabled: true\n")
        f.close()
if heisenberg_bridge:
    with open('{}/foo.yml'.format(yml_path), 'a') as f:
        heisenbridge = [
            "matrix_heisenbridge_enabled: true\n",
            'matrix_heisenbridge_owner: "{}"\n'.format(heisenbridge_owner),
            "matrix_heisenbridge_identd_enabled: true\n"
        ]
        f.writelines(heisenbridge)
        f.close()
if appservice_discord_bridge:
    with open('{}/foo.yml'.format(yml_path), 'a') as f:
        appservice = [
            "matrix_appservice_discord_enabled: true\n",
            "matrix_appservice_discord_bridge_enableSelfServiceBridging: true\n",
            'matrix_appservice_discord_client_id: "{}"\n'.format(appservice_discord_brige_client_id),
            'matrix_appservice_discord_bot_token: "{}"\n'.format(appservice_discord_bridge_token)
        ]
        f.writelines(appservice)
        f.close()

if http_port is not None:
    with open('{}/foo.yml'.format(yml_path), 'a') as f:
        ports = [
            "matrix_nginx_proxy_container_http_host_bind_port: '{}'\n".format(http_port),
            "matrix_nginx_proxy_container_https_host_bind_port: '{}'\n".format(https_port)
        ]
        f.writelines(ports)
        f.close()


os.system("just roles")
os.system("just install-all")
