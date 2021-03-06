#!/usr/bin/env python
'''
*********************************************************
Copyright @ 2015 EMC Corporation All Rights Reserved
*********************************************************
'''
# -*- coding: utf-8 -*-

"""
Test KCS function
    - local fru can work
    - local lan can work
    - local sensor can work
    - local sel can work
    - local sdr can work
    - local user can work
"""
import unittest
import os
import yaml
from infrasim import VM_DEFAULT_CONFIG
from infrasim import qemu
from infrasim import model
import time
import paramiko


class test_kcs(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_img_file = "{}/kcs.img".\
            format(os.environ['HOME'])
        if os.path.exists(test_img_file) is False:
            os.system("wget -c \
                https://github.com/InfraSIM/test/raw/master/image/kcs.img \
                -O {}".format(test_img_file))

        if os.path.exists(test_img_file) is False:
            return

        os.system("touch test.yml")
        with open(VM_DEFAULT_CONFIG, 'r') as f_yml:
            self.conf = yaml.load(f_yml)
        self.conf["name"] = "test"
        self.conf["compute"]["storage_backend"] = [{
            "controller": {
                "type": "ahci",
                "max_drive_per_controller": 6,
                "drives": [{"size": 8, "file": test_img_file}]
            }
        }]
        with open("test.yml", "w") as yaml_file:
            yaml.dump(self.conf, yaml_file, default_flow_style=False)

        node = model.CNode(self.conf)
        node.init()
        node.precheck()
        node.start()

        time.sleep(3)
        import telnetlib
        tn = telnetlib.Telnet(host="127.0.0.1", port=2345)
        tn.read_until("(qemu)")
        tn.write("hostfwd_add ::2222-:22\n")
        tn.read_until("(qemu)")
        tn.close()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        paramiko.util.log_to_file("filename.log")
        while True:
            try:
                ssh.connect("127.0.0.1", port=2222, username="root",
                    password="root", timeout=120)
                ssh.close()
                break
            except paramiko.SSHException:
                time.sleep(1)
                continue
            except Exception as e:
                assert False

        time.sleep(3)

    @classmethod
    def tearDownClass(self):
        test_img_file = "{}/kcs.img".\
            format(os.environ['HOME'])
        node = model.CNode(self.conf)
        node.init()
        node.stop()
        node.terminate_workspace()
        self.conf = None
        os.system("rm -rf test.yml")
        os.system("rm -rf {}".format(test_img_file))

    def test_qemu_local_fru(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool fru print")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "QTFCJ052806D1" in lines

    def test_qemu_local_lan(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool lan print")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "Auth Type" in lines

    def test_qemu_local_sensor(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool sensor list")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "CPU_0" in lines

    def test_qemu_local_sdr(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool sdr list")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "CPU_0" in lines

    def test_qemu_local_sel(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool sel list")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "Pre-Init" in lines

    def test_qemu_local_user(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("127.0.0.1", port=2222, username="root", password="root", timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ipmitool user list")
        while not stdout.channel.exit_status_ready():
            pass
        lines = stdout.channel.recv(2048)
        print lines
        ssh.close()
        assert "admin" in lines
