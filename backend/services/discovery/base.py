from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDiscovery(ABC):
    @abstractmethod
    def find_company_website(self, company_name: str) -> str:
        """
        Finds the official website for a given company name.
        Returns the URL as a string, or None if not found.
        """
        pass

    @abstractmethod
    def discover_companies(self, industry: str, country: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Discovers companies in a given industry and country.
        Returns a list of dictionaries with 'company' and 'website' keys.
        """
        pass
