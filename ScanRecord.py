class ScanRecord:
    def __init__(
        self,
        ipAddress='',
        port='',
        service='',
        state='',
        proto='',
        banner='',
        country='',
        city='',
        ):
        self.ipAddress = ipAddress
        self.port = port
        self.service = service
        self.state = state
        self.proto = proto
        self.banner = banner
        self.country = country
        self.city = city

    def __repr__(self):
        return self.ipAddress + " " + self.port + " " + self.service + " " + self.state + " " + self.proto + " " + self.banner

    def __str__(self):
        return self.ipAddress + " " + self.port + " " + self.service + " " + self.state + " " + self.proto + " " + self.banner
