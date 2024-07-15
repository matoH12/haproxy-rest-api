
# HAProxy Setup and Configuration

## Introduction
This project involves setting up and configuring HAProxy, a high-availability load balancer and proxy server for TCP and HTTP-based applications. HAProxy is widely used for its performance, reliability, and advanced features. This README provides step-by-step instructions to install, configure, and manage HAProxy in your environment.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Contributors](#contributors)
- [License](#license)

## Installation
To install HAProxy, follow these steps:

1. **Update your package list:**
   ```sh
   sudo apt-get update
   ```

2. **Install HAProxy:**
   ```sh
   sudo apt-get install haproxy
   ```

3. **Enable HAProxy to start on boot:**
   ```sh
   sudo systemctl enable haproxy
   ```

## Configuration
1. **Edit the HAProxy configuration file:**
   ```sh
   sudo nano /etc/haproxy/haproxy.cfg
   ```

2. **Basic Configuration Example:**
   ```plaintext
   global
       log /dev/log    local0
       log /dev/log    local1 notice
       chroot /var/lib/haproxy
       stats socket /run/haproxy/admin.sock mode 660 level admin
       stats timeout 30s
       user haproxy
       group haproxy
       daemon

   defaults
       log     global
       mode    http
       option  httplog
       option  dontlognull
       timeout connect 5000
       timeout client  50000
       timeout server  50000

   frontend http-in
       bind *:80
       default_backend servers

   backend servers
       server server1 127.0.0.1:8000 maxconn 32
   ```

3. **Restart HAProxy to apply the configuration:**
   ```sh
   sudo systemctl restart haproxy
   ```

## Usage
- **Start HAProxy:**
  ```sh
  sudo systemctl start haproxy
  ```

- **Check HAProxy status:**
  ```sh
  sudo systemctl status haproxy
  ```
- **Create private key:**
  ```sh
  openssl genpkey -algorithm RSA -out /etc/ssl/private/selfsigned.key
  ```
- **Create self-signed cert:**
  ```sh
  openssl req -new -x509 -key /etc/ssl/private/selfsigned.key -out /etc/ssl/certs/selfsigned.crt -days 365 -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
  ```

## Features
- Load balancing for TCP and HTTP applications
- SSL termination
- Health checks
- HTTP compression
- Stickiness and persistence
- Advanced logging and monitoring

## Dependencies
- **Operating System:** Linux (Debian-based recommended)
- **Packages:** 
  - HAProxy
  - Systemd (for managing services)

## Troubleshooting
- **Logs:** Check logs in `/var/log/haproxy.log` for troubleshooting.
- **Configuration errors:** Use the following command to test configuration before restarting:
  ```sh
  sudo haproxy -f /etc/haproxy/haproxy.cfg -c
  ```

## Examples
### Using REST API:
- **Pridanie novej domény:**
  ```sh
  curl -X POST http://localhost:5000/add_domain -H "Content-Type: application/json" -d '{"domain": "moja.domena.sk", "ip": "192.168.1.1"}'
  ```

- **Pridanie ďalšej domény:**
  ```sh
  curl -X POST http://localhost:5000/add_domain -H "Content-Type: application/json" -d '{"domain": "a.moja.domena.sk", "ip": "192.168.1.2"}'
  ```

- **Odstránenie domény:**
  ```sh
  curl -X POST http://localhost:5000/remove_domain -H "Content-Type: application/json" -d '{"domain": "moja.domena.sk"}'
  ```

- **Výpis všetkých domén:**
  ```sh
  curl -X GET http://localhost:5000/list_domains
  ```

- **Kontrola stavu HAProxy:**
  ```sh
  curl -X GET http://localhost:5000/check_status
  ```

Týmto spôsobom môžete dynamicky pridávať a odstraňovať domény, získavať zoznam všetkých aktuálne nakonfigurovaných domén a kontrolovať stav HAProxy pomocou API a HAProxy.

## Contributors
- Martin Hasin [@matoh12](https://github.com/matoh12)

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
