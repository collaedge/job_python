import psutil
import logging
import time

def run():
    # logging.basicConfig(filename="cpu_usage.log", level=logging.DEBUG)
    logger = logging.getLogger()
    hdlr = logging.FileHandler('cpu_usage.log')
    # formatter = logging.Formatter('%(asctime)s  -  %(message)s')
    # hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    while 1:
        cpu_usage = psutil.cpu_percent(interval=1)
        t = time.time()
        info = str(t) + '-' + str(cpu_usage)
        logger.info(info)

run()