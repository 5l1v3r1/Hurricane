#!/usr/bin/python
# -*- coding: utf-8 -*-

# Server files decryption key
HURRICANE_KEY  = ""

# Database settings
MYSQL_DBHOST = ""
MYSQL_DBNAME = ""
MYSQL_DBUSER = ""
MYSQL_DBPASS = ""

# Server files
HURRICANE_SERVER = 'https://raw.githubusercontent.com/LimerBoy/Hurricane/master/files/'



# Import modules
import os
import time
import zipfile

# Check root access
if os.getuid() != 0:
    print('[!] Please run script as root')
    exit()

# Errors list
errors = []

# Start timer
timer = time.time();

# Download server files and unpack
if not os.path.exists('server.zip'):
    os.system('wget ' + HURRICANE_SERVER + 'server.zip')

# Download database
if not os.path.exists('database.sql'):
    os.system('wget ' + HURRICANE_SERVER + 'database.sql')

# Unpack server files
with zipfile.ZipFile('server.zip', 'r') as server_files:
    try:
        server_files.extractall(path = '/var/www/html', pwd = bytes(HURRICANE_KEY).encode('utf-8'))
    except RuntimeError:
        time.sleep(4.30)
        print('[!] Wrong encryption password!')
        os.remove('server.zip')
        exit()
    else:
        print('[+] Successfuly decrypted server files..')
        time.sleep(0.30)

# Execute some commands
for command in (
    'apt update -y',
    'apt upgrade -y',
    ):
    print('\n[~] Preparing updating...')
    status_code = os.system(command)
    if status_code == 0:
        print('[+] System updated!')
    else:
        print('[-] Some problems while updating system...')
        errors.append('CMD     : ' + command + ', code: ' + str(status_code))

# Install dependecies
for package in (
    'unzip',
    'php',
    'apache2',
    'mysql-server',
    'phpmyadmin',
    ):
    print('\n[~] Preparing installation ' + package + '...')
    status_code = os.system('apt install ' + package + ' -y')
    if status_code == 0:
        print('[+] Package ' + package + ' installed successfuly!')
        time.sleep(0.30)
    else:
        print('[-] Problems while installation ' + package + ', returned code: \"' + str(status_code) + '\"')
        errors.append('APT     : ' + package + ', code: ' + str(status_code))
        time.sleep(1.50)

# MYSQL
for command in (
        'mysql -e \"CREATE USER \'' + MYSQL_DBUSER + '\'@\'' + MYSQL_DBHOST + '\' IDENTIFIED BY \'' + MYSQL_DBPASS + '\';\"',
        'mysql -e \"GRANT  SELECT, INSERT, UPDATE, DELETE ON * . * TO \'' + MYSQL_DBUSER + '\'@\'' + MYSQL_DBHOST + '\';\"',
        'mysql -e \"FLUSH PRIVILEGES;\"',
        'mysql -u ' + MYSQL_DBUSER + ' -p' + MYSQL_DBPASS + ' -e \"CREATE DATABASE ' + MYSQL_DBNAME + ';\"',
        'mysql -u ' + MYSQL_DBUSER + ' -p' + MYSQL_DBPASS + ' ' + MYSQL_DBNAME + ' < database.sql',
    ):
    # MYSQL
    # Create user, set password, add privileges, create database.
    status_code = os.system(command)
    if status_code == 0:
        print('[+] Setting up mysql...')
        time.sleep(0.20)
    else:
        print('\n[-] Problems with mysql command \"' + command + '\", returned code: \"' + str(status_code) + '\"')
        errors.append('MYSQL   : ' + command + ', code: ' + str(status_code))
        time.sleep(1.50)
# Delete tempfile
os.remove('database.sql')

# Configure apache2
with open('/etc/apache2/sites-enabled/000-default.conf', 'w') as file:
    # APACHE2
    # Update config
    print('[~] Configuring apache2')
    try:
        file.write(
"""
LoadModule headers_module modules/mod_headers.so
LoadModule rewrite_module modules/mod_rewrite.so

<VirtualHost *:80>
        ServerAdmin LimerBoyTV@gmail.com
        DocumentRoot /var/www/html
        <Directory "/var/www/html">
                Options FollowSymLinks
                AllowOverride All
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
""")
    except Exception as error:
        print('[-] Something went wrong while configuring apache')
        error.append('APACHE2 : Error while writing 000-default.conf\n         ' + str(error.args))

for command in (
        'a2enmod headers',
        'a2enmod rewrite',
        'service apache2 restart',
        'systemctl -l --no-pager status apache2',
        'chmod 777 /var/www/html',
        'chown -R www-data:www-data /var/www/html/',
    ):
    # APACHE2
    # Restart, Check status
    status_code = os.system(command)
    if status_code == 0:
        print('[+] Setting up apache2...')
        time.sleep(0.75)
    else:
        print('\n[-] Problems with apache2 command \"' + command + '\", returned code: \"' + str(status_code) + '\"')
        errors.append('APACHE2 : ' + command + ', code: ' + str(status_code))
        time.sleep(1.50)

# Show all errors
if errors:
    print('\n   *  ERRORS LIST:\n   |')
    for error in errors:
        print('   |--> ' + error)
    print    ('   |_____________\n[?] All errors count: ' + str(len(errors)))
else:
    print('\n[+] Installed successfuly!\n    All errors count: ' + str(len(errors)))

print('[?] Time elapsed: ' + str(round(time.time() - timer)) + ' secounds.')
print('[!] Now please edit: /var/www/html/scripts/settings.php file.')

# Created by LimerBoy!
