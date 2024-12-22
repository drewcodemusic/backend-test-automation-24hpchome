from .base_api import BaseAPI
from config.config import TestConfig

class OnsaleAPI(BaseAPI):
    def get_onsale_products(self):
        return self._get(TestConfig.Endpoints.ONSALE)