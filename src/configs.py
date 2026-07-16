import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RUN_NEWS_CLASSIFIER = True
RUN_LLM_NEWS_SEARCH = True

PERIODICITY = "WEEKLY"
ANALYSIS_LOOKBACK = 1
BASELINE_LOOKBACK = 10

LLM_MAX_CALLS = 20
LLM_MIN_BATCH_SIZE = 5
LLM_MAX_BATCH_SIZE = 20

SEARCH_PROVIDER = "gemini"
CLASSIFIER_PROVIDER = "gemini"

GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]

GEMINI_API_KEYS = [
    key.strip()
    for key in os.getenv("GEMINI_API_KEYS", "").split(",")
    if key.strip()
]

TOP_N = 20

BBG_HOST = "localhost"
BBG_PORT = 8194

NEWS_FIELDS = [
    "NEWS_NEG_SENTIMENT_COUNT",
    "NEWS_POS_SENTIMENT_COUNT",
    "NEWS_NEUTRAL_SENTIMENT_COUNT",
    "CHINESE_NEWS_NEG_SNTMNT_COUNT",
    "CHINESE_NEWS_POS_SNTMNT_COUNT",
    "CHINESE_NEWS_NEUTRL_SNTMNT_COUNT",
    "NEWS_HEAT_PUB_DNUMSTORIES",
    "NEWS_SENTIMENT_DAILY_AVG",
    "CHINESE_NEWS_SENTMNT_DAILY_AVG",
]

FINANCIAL_FIELDS = [
    "SALES_REV_TURN",
    "NET_INCOME",
    "EBITDA",
    "BS_TOT_ASSET",
    "BS_TOT_DEBT",
]

INPUT_DIR = Path("input")
INPUT_FILE = INPUT_DIR / "classified_company_list.xlsx"
