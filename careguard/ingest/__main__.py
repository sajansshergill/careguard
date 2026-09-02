from careguard.ingest.build_index import main

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build the CareGuard policy index")
    ap.add_argument("--source", default="data/policies/")
    main(ap.parse_args().source)
