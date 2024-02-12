from flask import Flask, render_template, request, redirect, send_file
import yaml
import subprocess
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def create_vpn():
    vars_data = {
        "firewall_ip": request.form['firewall_ip'],
        "username": request.form['username'],
        "password": request.form['password'],
        "pre_shared_key": request.form['pre_shared_key'],
        "vpn_zone": request.form['vpn_zone'],
        "vpn_destination": request.form['vpn_destination'],
        "ike_profile_name": request.form['ike_profile_name'],
        "ike_hash": request.form['ike_hash'],
        "ike_dh_group": request.form['ike_dh_group'],
        "ike_encryption": request.form['ike_encryption'],
        "ike_lifetime_seconds": request.form['ike_lifetime_seconds'],
        "ipsec_profile_name": request.form['ipsec_profile_name'],
        "ipsec_esp_authentication": request.form['ipsec_esp_authentication'],
        "ipsec_esp_encryption": request.form['ipsec_esp_encryption'],
        "ipsec_lifetime_seconds": request.form['ipsec_lifetime_seconds'],
        "ipsec_dh_group": request.form['ipsec_dh_group'],
        "local_address_interface": request.form['local_address_interface'],
        "local_ip": request.form['local_ip'],
        "peer_ip": request.form['peer_ip'],
        "firewall_rule_inbound": request.form['firewall_rule_inbound'],
        "firewall_rule_inbound_source": request.form['firewall_rule_inbound_source'],
        "firewall_rule_inbound_destination": request.form['firewall_rule_inbound_destination'],
        "firewall_rule_outbound": request.form['firewall_rule_outbound'],
        "firewall_rule_outbound_source": request.form['firewall_rule_outbound_source'],
        "firewall_rule_outbound_destination": request.form['firewall_rule_outbound_destination'],
        "ipsec_tunnel_name": request.form['ipsec_tunnel_name'],
        "proxy_id_local": request.form['proxy_id_local'],
        "proxy_id_remote": request.form['proxy_id_remote'],
        "proxy_id_protocol": request.form['proxy_id_protocol'],
        "tunnel_monitor": request.form['tunnel_monitor'],
        "tunnel_disabled": request.form['tunnel_disabled'],
        "ike_gateway_name": request.form['ike_gateway_name'],
        "tunnel_interface": request.form['tunnel_interface']
    }

    with open('vars.yml', 'w') as file:
        yaml.dump(vars_data, file)

    # Run the script to create the VPN configuration
    subprocess.run(['/usr/bin/python3', 'create_s2s_vpn.py'])

    # Generate PDF file
    pdf_content = generate_pdf(vars_data)
    return send_file(pdf_content, as_attachment=True, download_name='vpn_configuration.pdf')

def generate_pdf(vars_data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()



    text = f"""Dear Partner, Please find next the VPN Configuration Details:
    Pre-Shared Key: {vars_data['pre_shared_key']}
    IKE Hash: {vars_data['ike_hash']}
    IKE DH Group: {vars_data['ike_dh_group']}
    IKE Encryption: {vars_data['ike_encryption']}
    IKE Lifetime Seconds: {vars_data['ike_lifetime_seconds']}
    IPSec Profile Name: {vars_data['ipsec_profile_name']}
    IPSec ESP Authentication: {vars_data['ipsec_esp_authentication']}
    IPSec ESP Encryption: {vars_data['ipsec_esp_encryption']}
    IPSec Lifetime Seconds: {vars_data['ipsec_lifetime_seconds']}
    IPSec DH Group: {vars_data['ipsec_dh_group']}
    Local IP: {vars_data['local_ip']}
    Peer IP: {vars_data['peer_ip']}
    Proxy ID Local: {vars_data['proxy_id_local']}
    Proxy ID Remote: {vars_data['proxy_id_remote']}
    Proxy ID Protocol: {vars_data['proxy_id_protocol']}
    """

    # Add the VPN configuration details to the document
    p = Paragraph(text, styles["Normal"])
    doc.build([p])

    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    app.run(debug=True)
