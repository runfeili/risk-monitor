import logging
from datetime import datetime
from pathlib import Path


def setup_logger():

    log_dir = Path(__file__).parent.parent.parent / "logs"

    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"risk_monitor_{datetime.today():%Y%m%d}.log"

    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)-7s | %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )

    for name in [
        "google",
        "httpx",
        "urllib3",
        "google.genai",
        "google_genai",
        "httpx",
        "absl",
    ]:
        logging.getLogger(name).setLevel(logging.WARNING)
