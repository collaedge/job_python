import psutil
import logging
import time
import sys

class CPU:
    def __init__(self, pid):
        super().__init__()
        self.pid = pid

    def run(self):
        # logging.basicConfig(filename="cpu_usage.log", level=logging.DEBUG)
        logger = logging.getLogger()
        hdlr = logging.FileHandler('cpu_usage.log')
        # formatter = logging.Formatter('%(asctime)s  -  %(message)s')
        # hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.DEBUG)
        while 1:
            p = psutil.Process(self.pid)
            cpu_usage = psutil.cpu_percent(interval=2)
            t = time.time()
            info = str(t) + '-' + str(cpu_usage)
            logger.info(info)

if __name__ == "__main__":
    cpu=CPU(sys.argv[1])
    cpu.run()