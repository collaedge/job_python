import psutil
import logging

def run():
    # logging.basicConfig(filename="cpu_usage.log", level=logging.DEBUG)
    logger = logging.getLogger()
    hdlr = logging.FileHandler('cpu_usage.log')
    formatter = logging.Formatter('%(asctime)s  -  %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    while 1:
        cpu_usage = psutil.cpu_percent()
        logger.info(cpu_usage)

run()