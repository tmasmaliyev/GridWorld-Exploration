from .client import APIClient

import logging

class APIManager:
    def __init__(self) -> None:
        self.client = {}    

        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_client(self, label : str, client : APIClient) -> None:
        self.client.update({label : client})
    
    def get_client(self, label : str) -> APIClient:
        if label not in self.client:
            self.logger.error(f"Label : {label} is not registered as client !")
            raise
        
        return self.client.get(label)
