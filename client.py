__author__ = 'brendan'
import random
from uuid import uuid4
import pyudev
import time
import threading
import re
import redis

REDIS_CLIENT = redis.Redis()
hostrex = re.compile('(/.*:.*)?(\/host.*)?')


class UdevProcessListener(object):
    """
    Device Listener class, performs device filtering and reports change events to Redis param:qkey list
    """

    allowed_subsystems = ['scsi_host', 'scsi',  'usb']
    devpath_regex_str = '(/.*:.*)?(\/host.*)?'
    devpath_regex = re.compile(devpath_regex_str)

    def __init__(self, qkey=None):
        self.qkey = qkey
        self.rc = redis.StrictRedis()
        con = pyudev.Context()
        mon = pyudev.Monitor.from_netlink(con)
        self.observer = pyudev.MonitorObserver(mon, self.on_change)

    def start(self):
        self.observer.start()
        while True:
            self.rc.zremrangebyscore('ignore', 0, time.time() - 60)
            time.sleep(1)

    def on_change(self, action, device):
        if not self.ignore_device(device):
            self.rc.set(device.get('DEVPATH'), time.time())

    def ignore_device(self, device):
        """
        filter method for ignoring duplicate change events as seen on scsi block devices (Mount)
        """
        subsystem = device.subsystem
        if subsystem not in self.allowed_subsystems:
            return True

        devpath = self.get_filtered_devpath(device)
        ignored_devices = self.rc.zscan('ignore', match=devpath)
        print ignored_devices
        self.rc.zadd('ignore', '{}'.format(devpath), time.time())
        if devpath:
            if devpath in ignored_devices:
                return True
            else:
                if subsystem.startswith('scsi'):
                    self.rc.zadd('ignore', '{}'.format(devpath), time.time())
        return False

    def get_filtered_devpath(self, device):
        devpath = device.get('DEVPATH')
        if devpath:
            return self.devpath_regex.sub('', devpath).strip()
        return devpath

class UdevListener(threading.Thread):
    """
    Listener Thread implementing udev to update registered functions of USB change events
    doent update itself immediately, usb events simply set a dirty state to be picked up later
    """

    force_update_interval = 600
    monitor_loop_delay = 5

    def __init__(self):
        threading.Thread.__init__(self)
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.observer = pyudev.MonitorObserver(self.monitor, self.on_change)
        self.daemon = True
        self.last_updated = time.time()
        self.dirty = False
        self.ignore = dict()

    def on_change(self, action, device):
        subsystem = device.subsystem
        print device.get('DEVPATH')
        if subsystem not in ['scsi_host', 'scsi',  'usb']:
            return
        devpath = hostrex.sub('', device.get('DEVPATH'))
        print subsystem, devpath
        if not self.ignore.get(devpath) and subsystem.startswith('scsi'):
            self.ignore[devpath] = time.time()
            self.dirty = True
        elif self.ignore.get(devpath):
            delta_time = time.time() - self.ignore.get(devpath)
            if delta_time > 60:
                self.ignore[devpath] = time.time()
                print 'SETTING DIRTY TIMEOUT'
                self.dirty = True
            else:
                print 'IGNORING {}'.format(devpath)
        else:
            print 'SETTING DIRTY NORMAL'
            self.dirty = True

    def update(self):
        self.last_updated = time.time()
        self.dirty = False

    def on_timeout(self):
        print 'device timeout'
        self.q.put({
        'action': 'pull',
        'job_id': 'internal',
        'data': {
        }
        })
        self.update()

    def register(self, func):
            self.change_events.append(func)

    def callback(self):
        self.dirty = False
        print 'changed'
        for f in self.callbacks:
            f()

    def run(self):
        self.observer.start()
        while True:
            if self.dirty:
                self.last_updated = time.time()
                self.update()
            if self.deltatime > self.force_update_interval:
                self.last_updated = time.time()
                self.on_timeout()
                self.update()
            time.sleep(self.monitor_loop_delay)

    @property
    def deltatime(self):
        return time.time() - self.last_updated

def ran():
    while True:
        yield str(uuid4()), str(uuid4())


if __name__ == '__main__':
    u = UdevProcessListener(qkey='charger_mq')
    u.start()
    print u