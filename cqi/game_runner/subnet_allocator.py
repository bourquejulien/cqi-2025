import logging
from docker.models.networks import Network

class SubnetAllocator:
    subnet: str
    allocated: set[str]

    def __init__(self):
        self.subnet = "172.18"
        self.allocated = set()

    def _format(self, i: int) -> str:
        return f"{self.subnet}.{i}.0/24"

    def allocate(self):
        for i in range(1, 255):
            subnet = self._format(i) 
            if subnet not in self.allocated:
                self.allocated.add(subnet)
                return subnet
        return None

    def deallocate(self, subnet: str):
        if subnet in self.allocated:
            self.allocated.remove(subnet)
            return

        logging.warning(f"Subnet {subnet} not allocated")
    
    def deallocate_from_network(self, network: Network):
        subnet: str
        try:
            subnet = network.attrs["IPAM"]["Config"][0]["Subnet"]
        except:
            logging.error(f"Could not deallocate subnet from network: {network}")
        
        self.deallocate(subnet)
