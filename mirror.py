import configparser
import os
import threading
import time
import logging

mirror = []
config = {}
logger = None


def init():
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    sec = cf.sections()
    config['workers'] = cf.getint('config', 'workers')
    config['runners'] = 0
    for name in sec:
        if name != 'config' and name[0] != '#':
            if cf.get(name, 'type') == 'shell':
                mirror.append({
                    'name': name,
                    'type': cf.get(name, 'type'),
                    'command': cf.get(name, 'command'),
                    'interval': cf.getint(name, 'interval'),
                    'status': 0,
                    'time': 0,
                })


def runner():
    config['runners'] = config['runners'] + 1
    for work in mirror:
        if work['status'] <= 0 and int(time.time()) - work['time'] > work['interval']:
            logging.info('runner ' + str(config['runners']) + ' create')
            if work['status'] == 0:
                work['status'] = 1
            else:
                work['status'] = 1 - work['status']
            logging.info(work['name'] + ' is running')
            if work['type'] == 'shell':
                error = os.system(work['command'])
                if error == 0:
                    work['status'] = 0
                    work['time'] = int(time.time())
                    logging.info(work['name'] + ' success')
                else:
                    if work['status'] % 5 == 0:
                        work['time'] = int(time.time())
                    logging.warning(work['name'] + ' error on ' + str(work['status']))
                    work['status'] = -work['status']
            logging.info(work['name'] + ' next update time ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                                                             time.localtime(
                                                                                 int(work['time']) + work['interval'])))
            logging.info('runner ' + str(config['runners']) + ' destroy')
            break
    config['runners'] = config['runners'] - 1


if __name__ == '__main__':
    os.environ['TZ'] = 'Asia/Shanghai'
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info('INIT CONFIG')
    init()
    logging.info('INIT RUNNER')
    while True:
        if config['runners'] < config['workers']:
            threading.Thread(target=runner).start()
        time.sleep(60)
