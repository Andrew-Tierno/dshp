#!/usr/bin/python3.8
import socket, sys, json, os, subprocess, datetime, time
import threading
import click
from typing import List

class SocketListener(threading.Thread):
    def __init__(self, port, interface):
        threading.Thread.__init__(self)
        self.port = port
        self.interface = interface
        # bind socket and start listening
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.error = False
        print("Socket on host: " + interface + " port: " + str(port) + " created.")
        try:
            self.sock.bind((self.interface, self.port))
        except Exception as msg:
            print("Bind failed. Error Code : " + str(msg))
            self.error = True
            return
        print("Socket on host: " + interface + " port: " + str(port) + " bind complete.")
        self.sock.listen(5)
        print("Socket on host: " + interface + " port: " + str(port) + " now listening.")

    def run(self):
        if self.error:
            print("Skipping listener on port " + str(self.port))
            return
        while True:
            conn, addr = self.sock.accept()
            offender_ip = addr[0]
            print("attempted connection from " + offender_ip)

REQUIRED_KEYS = [("port_list", List), ("host", str)]
def parse_config(path):
    try:
        config = json.load(open(path))
    except Exception as error:
        print("Failed to parse the config file. Error: " + error)
        sys.exit(1)
    for key, key_type in REQUIRED_KEYS:
        if not key in config:
            raise Exception("Invalid config provided-- missing field: " + key)
        if not isinstance(config[key], key_type):
            raise Exception("Invalid config provided-- field " + key + " must be of type " + str(key_type))
    return config

@click.command()
@click.option('--config_file',
                '--config',
                help="Specifies the configuration file path.",
                default="conf.json",
                type=str)
def main(config_file):
    config = parse_config(config_file)
    socket_threads = [SocketListener(port, config["host"]) for port in config["port_list"]]
    for t in socket_threads:
        t.daemon = True
    [t.start() for t in socket_threads]
    [t.join() for t in socket_threads]

if __name__ == "__main__":
    main()