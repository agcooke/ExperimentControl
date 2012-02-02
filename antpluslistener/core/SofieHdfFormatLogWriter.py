class LogWriter(object):
    def __init__(self, filename=''):
        self.packer = msgpack.Packer()
        self.is_open = False
        self.open(filename)

    def __del__(self):
        if self.is_open:
            self.fd.close()

    def open(self, filename=''):
        if filename == '':
            filename = datetime.datetime.now().isoformat() + '.ant'
        self.filename = filename

        if self.is_open == True:
            self.close()

        self.fd = open(filename, 'w')
        self.is_open = True
        self.packer = msgpack.Packer()

        header = ['ANT-LOG', 0x01]  # [MAGIC, VERSION]
        self.fd.write(self.packer.pack(header))

    def close(self):
        if self.is_open:
            self.fd.close()
            self.is_open = False

    def _logEvent(self, event, data=None):
        ev = [event, int(time.time()), data]

        if data is None:
            ev = ev[0:-1]
        elif len(data) == 0:
            return

        self.fd.write(self.packer.pack(ev))

    def logOpen(self):
        self._logEvent(EVENT_OPEN)

    def logClose(self):
        self._logEvent(EVENT_CLOSE)

    def logRead(self, data):
        self._logEvent(EVENT_READ, data)

    def logWrite(self, data):
        self._logEvent(EVENT_WRITE, data)
