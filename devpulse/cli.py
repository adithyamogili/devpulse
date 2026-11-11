import argparse
from devpulse.ingest import ingest

def main():
    parser = argparse.ArgumentParser(prog="devpulse")
    subs = parser.add_subparsers(dest="command", required=True)
    cmd = subs.add_parser("ingest", help="Extract GitHub data to MinIO and Kafka")
    cmd.add_argument("--repo", action="append", dest="repositories")
    cmd.add_argument("--max-pages", type=int, default=1)
    args = parser.parse_args()
    if args.max_pages < 1: parser.error("--max-pages must be >= 1")
    result = ingest(args.repositories, args.max_pages)
    print(f"Completed ingestion for {len(result)} repositories")

if __name__ == "__main__": main()
