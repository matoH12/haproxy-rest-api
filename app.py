from flask import Flask, request, jsonify
import os
import logging
import re
import subprocess

app = Flask(__name__)

# Nastavenie logovania
logging.basicConfig(level=logging.INFO)

# Konfiguračný súbor HAProxy
haproxy_config_path = '/etc/haproxy/haproxy.cfg'

def add_backend(domain, ip):
    try:
        with open(haproxy_config_path, 'r') as f:
            config = f.readlines()

        # Pridanie ACL a použitie backendu pre novú doménu vo frontend sekcii
        frontend_index = next(i for i, line in enumerate(config) if 'frontend http_front' in line)
        config.insert(frontend_index + 1, f'    acl host_{domain.replace(".", "_")} hdr(host) -i {domain}\n')
        config.insert(frontend_index + 2, f'    use_backend bk_{domain.replace(".", "_")} if host_{domain.replace(".", "_")}\n')

        # Pridanie nového backendu na koniec konfiguračného súboru
        config.append(f'\nbackend bk_{domain.replace(".", "_")}\n')
        config.append(f'    server {domain.replace(".", "_")}_server {ip}:80\n')

        with open(haproxy_config_path, 'w') as f:
            f.writelines(config)

        # Reštartovanie HAProxy, aby sa nové nastavenia prejavili
        os.system('sudo systemctl reload haproxy')

        logging.info(f"Added backend for domain: {domain} -> {ip}")
        return {"message": "Backend added successfully"}
    except Exception as e:
        logging.error(f"Failed to add backend: {e}")
        return {"error": "Failed to add backend"}

def remove_backend(domain):
    try:
        with open(haproxy_config_path, 'r') as f:
            config = f.readlines()

        # Odstránenie ACL a použitia backendu vo frontend sekcii
        config = [line for line in config if f'host_{domain.replace(".", "_")}' not in line]

        # Odstránenie backend sekcie pre danú doménu
        start_index = next(i for i, line in enumerate(config) if f'backend bk_{domain.replace(".", "_")}' in line)
        end_index = start_index + 2  # Predpokladáme, že backend sekcia má 2 riadky
        config = config[:start_index] + config[end_index:]

        with open(haproxy_config_path, 'w') as f:
            f.writelines(config)

        # Reštartovanie HAProxy, aby sa nové nastavenia prejavili
        os.system('sudo systemctl reload haproxy')

        logging.info(f"Removed backend for domain: {domain}")
        return {"message": "Backend removed successfully"}
    except Exception as e:
        logging.error(f"Failed to remove backend: {e}")
        return {"error": "Failed to remove backend"}

def list_backends():
    try:
        with open(haproxy_config_path, 'r') as f:
            config = f.readlines()

        # Vyhľadanie všetkých backend sekcií a extrakcia domén a IP adries
        backends = {}
        for i, line in enumerate(config):
            match = re.match(r'backend bk_(\S+)', line)
            if match:
                domain_key = match.group(1).replace("_", ".")
                ip_match = re.match(r'\s+server \S+ (\S+):80', config[i + 1])
                if ip_match:
                    ip_address = ip_match.group(1)
                    backends[domain_key] = ip_address

        logging.info("Listed all backends")
        return {"domains": backends}
    except Exception as e:
        logging.error(f"Failed to list backends: {e}")
        logging.exception("Exception details:")
        return {"error": "Failed to list backends"}

def check_haproxy_status():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'haproxy'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": "HAProxy is running"}
        else:
            return {"status": "error", "message": "HAProxy is not running"}
    except Exception as e:
        logging.error(f"Failed to check HAProxy status: {e}")
        return {"status": "error", "message": "Failed to check HAProxy status"}

@app.route('/add_domain', methods=['POST'])
def add_domain():
    data = request.get_json()
    domain = data.get('domain')
    ip = data.get('ip')

    if not domain or not ip:
        return jsonify({"error": "Missing required parameters"}), 400

    result = add_backend(domain, ip)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result), 201

@app.route('/remove_domain', methods=['POST'])
def remove_domain():
    data = request.get_json()
    domain = data.get('domain')

    if not domain:
        return jsonify({"error": "Missing required parameter: domain"}), 400

    result = remove_backend(domain)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result), 200

@app.route('/list_domains', methods=['GET'])
def list_domains():
    result = list_backends()
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result), 200

@app.route('/check_status', methods=['GET'])
def check_status():
    result = check_haproxy_status()
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
