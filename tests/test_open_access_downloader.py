import os
import pytest
from unittest import mock
from src.OpenAccessDownloader import OpenAccessDownloader

import sys
print("\n".join(sys.path))



@pytest.fixture
def downloader(tmp_path):
    return OpenAccessDownloader(email="test@example.com", output_dir=tmp_path)

def test_resolve_stub(monkeypatch, downloader):
    dois = ["10.fake/001", "10.fake/002"]

    def fake_get(url, params, timeout):
        class FakeResp:
            def ok(self): return True
            def json(self):
                return {
                    "best_oa_location": {
                        "url_for_pdf": f"https://fakepdf.org/{url.split('/')[-1]}.pdf"
                    }
                }
        return FakeResp()

    monkeypatch.setattr(downloader.session, "get", fake_get)

    urls = downloader.resolve(dois)
    assert urls == [
        "https://fakepdf.org/001.pdf",
        "https://fakepdf.org/002.pdf"
    ]

def test_download_stub(monkeypatch, downloader):
    urls = [
        "https://fakepdf.org/fake1.pdf",
        "https://fakepdf.org/fake2.pdf"
    ]

    # Fake requests.get
    def fake_get(url, timeout=60, stream=True):
        class FakeResp:
            def raise_for_status(self): pass
            def iter_content(self, chunk_size): return [b"FAKE_DATA"]
        return FakeResp()

    monkeypatch.setattr(downloader.session, "get", fake_get)

    # Run download
    downloader.download(urls)

    files = os.listdir(downloader.output_dir)
    assert len(files) == 2
    assert all(fname.endswith(".pdf") for fname in files)

