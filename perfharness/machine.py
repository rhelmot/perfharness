import platform
import os
import subprocess
import psutil
import re
import time
import gc

from .config import format_size, parse_size

# https://stackoverflow.com/questions/4842448/getting-processor-information-in-python
def get_processor_name():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        all_info = open('/proc/cpuinfo').read()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub( ".*model name.*:", "", line,1).strip()
    return ""

def get_os_name():
    if platform.system() == "Linux":
        import distro
        return distro.name(pretty=True)

    return '%s %s' % (platform.system(), platform.release())

def fingerprint_machine():
    return {
        'python': '%s %s' % (platform.python_implementation(), platform.python_version()),
        'hostname': platform.node(),
        'os': get_os_name(),
        'cpu': get_processor_name(),
        'cpu_count': '%d,%d' % (psutil.cpu_count(logical=True), psutil.cpu_count(logical=False)),
        'memory_size': format_size(round(psutil.virtual_memory().total)),
    }

def check_load(config):
    gc.collect()

    cpu_percent_less_than = int(config["cpu_percent_less_than"])
    mem_available_greater_than = parse_size(config["mem_available_greater_than"])
    battery = psutil.sensors_battery()
    if battery is not None and not battery.power_plugged:
        raise Exception("Cannot run tests unplugged from power")
    if psutil.virtual_memory().available < mem_available_greater_than:
        raise Exception("Cannot run tests with less than %s memory available" % format_size(mem_available_greater_than))
    for _ in range(10):
        if psutil.cpu_percent(1) < cpu_percent_less_than:
            return
        print("Cpu utilization too high, sleeping...")
        time.sleep(10)

    raise Exception("Cannot run tests with cpu utilization higher than %d%%" % cpu_percent_less_than)
