from .http import HTTPMethod
import requests, os

from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException

from typing import Optional, Dict, Union, Any
import logging

class APIClient:
    def __init__(
            self, 
            base_url : str,
            headers : Optional[Dict[str, str]],
            retries : int = 3,
            backoff_factor : float = 0.3,
            timeout : Union[int, float] = 15
    ) -> None:
        self.base_url = base_url
        self.session = requests.Session()

        self.timeout = timeout
        self.session.headers.update(headers or {})

        retry_strategy = Retry(
            total = retries,
            backoff_factor = backoff_factor,
            status_forcelist = [429, 500, 502, 503, 504],
            allowed_methods = [method.name for method in HTTPMethod]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('https://', adapter)

        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _request(self, method : HTTPMethod, endpoint : str, **kwargs) -> Any:
        url = self.base_url

        if endpoint.lstrip('/'):
            url = os.path.join(
                self.base_url, 
                endpoint.lstrip('/')
            )

        try:
            response = self.session.request(
                method = method.name,
                url = url,
                timeout = self.timeout,
                **kwargs   
            )
            response.raise_for_status()

            return response.json()
        except RequestException as e:
            self.logger.error(f"Request failed : {e}")
            raise


    def get(self, endpoint : str, params : Dict[str, Any] = None, **kwargs) -> Any:
        return self._request(
            method = HTTPMethod.GET, 
            endpoint = endpoint,
            params = params,
            **kwargs
        )
    
    def post(self, endpoint : str, data : Any = None, json : Any = None, **kwargs) -> Any:
        return self._request(
            method = HTTPMethod.POST,
            endpoint = endpoint,
            data = data,
            json = json,
            **kwargs
        )