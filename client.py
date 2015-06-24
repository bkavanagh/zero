__author__ = 'brendan'
import random
from uuid import uuid4
import pyudev
import time
import threading
import re
import redis
import json

class UdevProcessListener(object):
    """
    Device Listener class, performs device filtering and reports change events to Redis param:qkey list
    """
    monitor_loop = 15
    force_update_interval = 600
    allowed_subsystems = ['scsi_host', 'scsi',  'usb']
    devpath_regex_str = '(/.*:.*)?(\/host.*)?'
    devpath_regex = re.compile(devpath_regex_str)

    def __init__(self, qkey=None):
        self.dirty = True
        self.qkey = qkey
        self.rc = redis.Redis()
        con = pyudev.Context()
        mon = pyudev.Monitor.from_netlink(con)
        self.observer = pyudev.MonitorObserver(mon, self.on_change)
        self.last_updated = time.time()

    @property
    def deltatime(self):
        return time.time() - self.last_updated

    def start(self):
        self.observer.start()
        while True:
            self.cleanup_ignored_devices()
            if self.dirty:
                self.update()
            if self.deltatime > self.force_update_interval:
                self.force_update()
            time.sleep(self.monitor_loop)

    def cleanup_ignored_devices(self):
        self.rc.zremrangebyscore('ignore', 0, time.time() - self.monitor_loop)

    def on_change(self, action, device):
        if not self.ignore_device(device):
            self.dirty = True

    def update(self):
        self.last_updated = time.time()
        self.dirty = False
        self.push_event('device')

    def force_update(self):
        self.last_updated = time.time()
        self.dirty = False
        self.push_event('pull')

    def push_event(self, event):
        data = {
        'action': event,
        'job_id': 'internal',
        'data': {

            }
        }
        self.rc.rpush(self.qkey, json.dumps(data))

    def ignore_device(self, device):
        """
        filter method for ignoring duplicate change events as seen on scsi block devices (Mount)
        """
        subsystem = device.subsystem

        if subsystem not in self.allowed_subsystems:
            return True
        devpath = self.get_filtered_devpath(device)
        ignored_devices = [x[0] for x in self.rc.zscan('ignore', match=devpath)[1]]
        if devpath:
            if devpath in ignored_devices:
                return True
            else:
                self.rc.zadd('ignore', '{}'.format(devpath), time.time())
        return False

    def get_filtered_devpath(self, device):
        devpath = device.get('DEVPATH')
        if devpath:
            return self.devpath_regex.sub('', devpath).strip()
        return devpath

if __name__ == '__main__':
    u = UdevProcessListener(qkey='charger_mq')
    u.start()
    print u