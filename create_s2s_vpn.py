import paramiko
import yaml
import time

def execute_ssh_command(ssh_client, command):
    ssh_client.send(command + "\n")
    time.sleep(1)
    output = ssh_client.recv(65535).decode()
    return output

def main():
    try:
        print("Loading variables from palo2.yml...")
        # Load variables from palo2.yml
        with open("palo2.yml", "r") as file:
            vars_data = yaml.safe_load(file)
        print("Variables loaded successfully!")

        print("Establishing SSH connection...")
        # Connect to the firewall via SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(vars_data["firewall_ip"], port=22, username=vars_data["username"], password=vars_data["password"])
        print("SSH connection established successfully!")

        # Start an interactive shell session
        shell = ssh_client.invoke_shell()

        # Wait for the shell to be ready
        while not shell.recv_ready():
            time.sleep(1)

        # Enter configuration mode
        output = execute_ssh_command(shell, "configure")
        print(output)

        # Configure Tunnel Interface
        command = "configure"
        output = execute_ssh_command(shell, command)
        
        command = f"set network interface tunnel units {vars_data['tunnel_interface']}"
        output = execute_ssh_command(shell, command)
        
        # Assign the Tunnel Interface to a new zone called "vpn_zone"
        command = f"set zone {vars_data['vpn_zone']} network layer3 {vars_data['tunnel_interface']}"
        output = execute_ssh_command(shell, command)
        
        # Assign the Tunnel Interface to the default Virtual Router
        command = f"set network virtual-router default interface {vars_data['tunnel_interface']}"
        output = execute_ssh_command(shell, command)


        # Exit configuration mode
        output = execute_ssh_command(shell, "exit")
        print(output)

        # Enter configuration mode again
        output = execute_ssh_command(shell, "configure")
        print(output)

        # Create Tunnel Interface
        output = execute_ssh_command(shell, f"set network interface {vars_data['tunnel_interface']} units {vars_data['tunnel_interface']} ipv6 enable no")
        print(output)

        # Assign Tunnel Interface to Zone
        command = f"set zone {vars_data['vpn_zone']} network layer3 {vars_data['tunnel_interface']}"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)

        # Create Static Route for VPN traffic
        command = f"set network virtual-router default routing-table ip static-route vpn interface {vars_data['tunnel_interface']} destination {vars_data['vpn_destination']}"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)

        # Create IKE Crypto Profile
        command = f"set network ike crypto-profiles ike-crypto-profiles {vars_data['ike_profile_name']}"
        output = execute_ssh_command(shell, command)
        
        command = f"set network ike crypto-profiles ike-crypto-profiles {vars_data['ike_profile_name']} hash {vars_data['ike_hash']}"
        output = execute_ssh_command(shell, command)
        
        command = f"set network ike crypto-profiles ike-crypto-profiles {vars_data['ike_profile_name']} dh-group {vars_data['ike_dh_group']}"
        output = execute_ssh_command(shell, command)
        
        command = f"set network ike crypto-profiles ike-crypto-profiles {vars_data['ike_profile_name']} encryption {vars_data['ike_encryption']}"
        output = execute_ssh_command(shell, command)
        
        command = f"set network ike crypto-profiles ike-crypto-profiles {vars_data['ike_profile_name']} lifetime seconds {vars_data['ike_lifetime_seconds']}"
        output = execute_ssh_command(shell, command)
        
 

        # Create IPSec Crypto Profile
        command = f"set network ike crypto-profiles ipsec-crypto-profiles {vars_data['ipsec_profile_name']}\n"
        command = f"set network ike crypto-profiles ipsec-crypto-profiles {vars_data['ipsec_profile_name']} lifetime seconds {vars_data['ipsec_lifetime_seconds']}\n"
        command += f"set network ike crypto-profiles ipsec-crypto-profiles {vars_data['ipsec_profile_name']} esp authentication {vars_data['ipsec_esp_authentication']} encryption {vars_data['ipsec_esp_encryption']} lifetime seconds {vars_data['ipsec_lifetime_seconds']} dh-group {vars_data['ipsec_dh_group']}"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)

        # Create IKE Gateway
        command = f"set network ike gateway {vars_data['ike_gateway_name']}\n"
        command += f"set network ike gateway {vars_data['ike_gateway_name']} authentication pre-shared-key key {vars_data['pre_shared_key']}\n"
        command += f"set network ike gateway {vars_data['ike_gateway_name']} protocol ikev1 ike-crypto-profile {vars_data['ike_profile_name']}\n"
        command += f"set network ike gateway {vars_data['ike_gateway_name']} local-address interface {vars_data['local_address_interface']} ip {vars_data['local_ip']}\n"
        command += f"set network ike gateway {vars_data['ike_gateway_name']} peer-address ip {vars_data['peer_ip']}\n"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)

        # Create Firewall Rules for VPN traffic
        command = f"set rulebase security rules {vars_data['firewall_rule_inbound']} to any from any source {vars_data['firewall_rule_inbound_source']} destination {vars_data['firewall_rule_inbound_destination']} source-user any category any application any service any hip-profiles any action allow\n"
        command += f"set rulebase security rules {vars_data['firewall_rule_outbound']} to any from any source {vars_data['firewall_rule_outbound_source']} destination {vars_data['firewall_rule_outbound_destination']} source-user any category any application any service any hip-profiles any action allow"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)

        # Create the IPSec Tunnel
        command = f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} auto-key ike-gateway {vars_data['ike_gateway_name']}\n"
        command += f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} auto-key proxy-id subnets local {vars_data['proxy_id_local']} remote {vars_data['proxy_id_remote']} protocol {vars_data['proxy_id_protocol']}\n"
        command += f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} auto-key ipsec-crypto-profile {vars_data['ipsec_profile_name']}\n"
        command += f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} tunnel-interface {vars_data['tunnel_interface']}\n"
        command += f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} tunnel-monitor enable {vars_data['tunnel_monitor']}\n"
        command += f"set network tunnel ipsec {vars_data['ipsec_tunnel_name']} disabled {vars_data['tunnel_disabled']}"
        print("Executing command:", command)
        output = execute_ssh_command(shell, command)
        print("Command output:", output)


        print("All tasks completed successfully!")

    except Exception as e:
        print("Error:", e)

    finally:
        ssh_client.close()

if __name__ == "__main__":
    main()
