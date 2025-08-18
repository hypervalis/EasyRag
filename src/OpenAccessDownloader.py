from .BaseDownloader import AbstractDownloader
from pathlib import Path
import os, time, requests
from urllib.parse import urlparse
from typing import List

class OpenAccessDownloader(AbstractDownloader):
    def __init__(self, email: str, output_dir: str = "./pdfs", delay: int = 2, limit : int = 50):
        self.email = email
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.session = requests.Session()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.limit = limit

    def search(self, query: str) -> List[str]:
        resp = self.session.get(
            "https://api.crossref.org/works",
            params={"query.bibliographic": query, "rows": self.limit},
            timeout=30
        )
        resp.raise_for_status()
        return [item.get("DOI") for item in resp.json()["message"]["items"] if item.get("DOI")]

    def resolve(self, dois: List[str]) -> List[str]:
        urls = []
        num_downloads = 0
        for doi in dois:
            if num_downloads > self.limit:
                break
            r = self.session.get(
                f"https://api.unpaywall.org/v2/{doi}",
                params={"email": self.email},
                timeout=30
            )
            if r.ok:
                data = r.json().get("best_oa_location") or {}
                pdf = data.get("url_for_pdf")
                if pdf:
                    urls.append(pdf)
                    num_downloads += 1
        return list(dict.fromkeys(urls))

    def download(self, urls: List[str]) -> List[str]:
        saved = []
        
        for i, url in enumerate(urls, 1):
            fname = os.path.basename(urlparse(url).path) or f"doc_{i}.pdf"
            dest = self.output_dir / fname
            if dest.exists():
                print(f"[{i}] exists -> skip")
                saved.append(str(dest))
                continue
            try:
                print(f"[{i}] downloading {url}")
                r = self.session.get(url, timeout=60, stream=True)
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(32_768):
                        f.write(chunk)
                saved.append(str(dest))
            except Exception as e:
                print("error:", e)
            time.sleep(self.delay)
        return saved

