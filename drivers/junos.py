from base import NetworkDriver

from jnpr.junos import Device
from jnpr.junos.utils.config import Config

def __execute_rpc__(conn, rpc_command):
    output = conn.rpc(str(rpc_command))

    if len(output.xpath('/rpc-reply/error')) > 0:
        raise Exception(output.tostring)

    return output


class JunOSDriver(NetworkDriver):

    def __init__(self, hostname, user, password):
        self.hostname = hostname
        self.user = user
        self.password = password
        self.device = Device(hostname, user=user, password=password)

    def open(self):
        self.device.open()
        self.device.bind( cu=Config )
        self.device.cu.lock()

    def close(self):
        self.device.cu.unlock()
        self.device.close()

    def load_candidate_config(self, filename=None, config=None):
        if filename is None:
            configuration = config
        else:
            with open(filename) as f:
                configuration = f.read()

        self.device.cu.load(configuration, format='text', overwrite=True)

    def compare_config(self):
        return self.device.cu.diff()

    def commit_config(self):
        self.device.cu.commit()

    def discard_config(self):
        self.device.cu.rollback(rb_id=0)

    def rollback(self):
        self.device.cu.rollback(rb_id=1)
        self.commit_config()
