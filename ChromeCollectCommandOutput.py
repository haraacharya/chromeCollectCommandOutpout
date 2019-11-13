import argparse
import os
import platform
import re
import sys
import time
import subprocess
from datetime import datetime
import logging
import logging.handlers
from os.path import expanduser


def check_if_remote_system_is_live(ip):
    hostname = ip
    print ("hostname is", hostname)
    try:
        response = os.system("ping -c 1 " + hostname)
    except:
        return False

    if response == 0:
        return True
    else:
        return False

def run_command(command, dut_ip, username="root", password="test0000"):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + username + "@" + dut_ip + " '" + command +  "'"
        print (sshpassCmd)
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        
        ## Wait for command to terminate. Get return returncode ##
        p_status = p.wait()
        # print ("Command output : ", output)
        # print ("Command exit status/return code : ", p_status)
        if p_status != 0:
            return False
        else:
            return output.decode('ascii')

def is_tool(name):
    """Check whether `name` is on PATH."""

    from distutils.spawn import find_executable

    return find_executable(name) is not None

  


if __name__ == "__main__":

    if not is_tool("sshpass"):
        dlogger.info ("sshpass is not installed. Please install sshpass with sudo apt-get install sshpass")
        dlogger.info ("Exiting test!")
        sys.exit(1)

    parser = argparse.ArgumentParser()

    parser.add_argument('--ip', dest='ip_address', help='provide remote system ip')
    parser.add_argument('--command', dest='cmd_to_run', default = "dmesg --level=err", help='Please mention the command to check in double quotes!')
    parser.add_argument('--total_duration', dest='total_duration', default = 360, help='How much time in MINUTES you want to run the command for')
    parser.add_argument('--interval', dest='interval', default = 1, help='every how many SECONDS you want to capture cmd output')
    args = parser.parse_args()

    cmd_to_run = args.cmd_to_run
    total_duration = int(args.total_duration)
    interval = int(args.interval)

    
    
    if args.ip_address:
        ip_address = args.ip_address
    else:
        ip_address = False
        dlogger.info ("check with --help or give cmd argument --ip <ip_address>")
        sys.exit(1)
        
    print ("system ip address is                                      :", ip_address)
    print ("Command to run                                            :", cmd_to_run)
    print ("capture command out duration (in minutes)                 :", total_duration)
    print ("Run command every (in seconds)                            :", interval)
    print ("**********************************************************")
    
        
    if (sys.version_info > (3, 0)):
        input("Press Enter to continue...")
    else:
        # raw_input("Press Enter to continue...")
        raw_input("Press Enter to continue...")
    
    chrome_debug_log_folder = os.getcwd() + "/cmdOutput_log"
    if not os.path.exists(chrome_debug_log_folder):
        os.makedirs(chrome_debug_log_folder)

    log_file_name = chrome_debug_log_folder + "/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_" + ip_address + ".log" 

    logging.basicConfig(filename= log_file_name, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    dlogger = logging.getLogger(__name__)
    dlogger.addHandler(handler)   

    total_duration_in_seconds = total_duration * 60
    total_duration_in_seconds_for_loop = int(total_duration_in_seconds/interval)
    dlogger.info ("******************************")
    dlogger.info ("******************************")
    dlogger.info ("started comand capture %d minutes" % (total_duration))
    dlogger.info ("******************************")
    dlogger.info ("******************************")

    if check_if_remote_system_is_live(ip_address):
        #add to ssh known host
        add_known_host_cmd = "ssh-keygen -f " + '"' + expanduser("~") + '/.ssh/known_hosts" ' + "-R " + ip_address
        print(add_known_host_cmd)
        os.system(add_known_host_cmd)
    else:
        print ("system with IP %s is not pingable. Exiting script."%(ip_address))
        sys.exit()

    for i in range(total_duration_in_seconds_for_loop):
   
        cmd_output = run_command(cmd_to_run, ip_address, username="root", password="test0000")
        dlogger.info (cmd_output)
        time.sleep(interval)
     
    dlogger.info ("******************************")
    dlogger.info ("******************************")
    dlogger.info ("Completed comand capture for: %d minutes" % (total_duration))
    dlogger.info ("Check capture command output in file: %s" % (log_file_name))

    dlogger.info ("******************************")
    dlogger.info ("******************************")
