import argparse
from pathlib import Path
from .OpenAccessDownloader import OpenAccessDownloader

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="easyrag-download",
        description="Download open-access PDFs via Crossref + Unpaywall."
    )
    p.add_argument("--email", required=True, help="Contact email for Unpaywall.")
    p.add_argument("--query", required=True, help="Bibliographic keyword(s) for Crossref.")
    p.add_argument("--out", default="./oa_pdfs", help="Output folder (default: ./oa_pdfs).")
    p.add_argument("--delay", type=int, default=2, help="Seconds between PDF downloads.")
    p.add_argument("--rows", type=int, default=1000, help="Crossref rows to fetch.")
    p.add_argument("--dry-run", action="store_true",
                   help="Search & resolve only; print PDF URLs without downloading.")
    p.add_argument("--limit", type=int, default=50, help="Maximum number of downloads")
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    dl = OpenAccessDownloader(email=args.email, output_dir=args.out, delay=args.delay, limit=args.limit)

    print(f"Searching Crossref for: {args.query}")
    dois = dl.search(args.query)
    print(f" {len(dois)} DOIs")

    print("Resolving OA links via Unpaywall...")
    urls = dl.resolve(dois)
    print(f" {len(urls)} PDF URLs")

    if args.dry_run:
        print("\n(DRY RUN) Resolved URLs:")
        for u in urls:
            print(u)
        return 0

    Path(args.out).mkdir(parents=True, exist_ok=True)
    print(f"Downloading to: {args.out}")
    saved = dl.download(urls)
    print(f"Saved {len(saved)} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

