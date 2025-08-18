from abc import ABC, abstractmethod
from typing import List

class AbstractDownloader(ABC):
    @abstractmethod
    def search(self, query: str) -> List[str]:
        """Search the data source and return a list of item IDs or URLs."""
        pass

    @abstractmethod
    def resolve(self, ids: List[str]) -> List[str]:
        """Turn item IDs into downloadable URLs."""
        pass

    @abstractmethod
    def download(self, urls: List[str]) -> List[str]:
        """Download and save the actual files. Return list of local paths."""
        pass

    def run(self, query: str) -> List[str]:
        """High-level entry point."""
        print(f"Searching for: {query}")
        ids = self.search(query)
        print(f"{len(ids)} results")

        print("Resolving links...")
        urls = self.resolve(ids)
        print(f" {len(urls)} resolved URLs")

        print("Downloading...")
        return self.download(urls)

