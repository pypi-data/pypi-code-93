class FirewallRule:
    def __init__(self, start_ip_address: str, end_ip_address: str, name: str):
        self.name = name
        self.start_ip_address = start_ip_address
        self.end_ip_address = end_ip_address
