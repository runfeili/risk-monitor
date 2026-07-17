import json
from pathlib import Path
from string import Template
from config import PROMPT_CONFIG

PROMPT_DIR = Path(__file__).parent / "prompts"


def load_prompt(name):

    filename = PROMPT_CONFIG[name]

    prompt_path = PROMPT_DIR / filename

    return prompt_path.read_text(encoding="utf-8")


def build_news_classifier_prompt(news_records):

    template = Template(load_prompt("news_classifier"))

    return template.substitute(
        news_records=json.dumps(
            news_records,
            ensure_ascii=False,
            indent=2,
        )
    )


def build_news_search_prompt(companies, start_date, end_date):
    companies_text = "\n".join(f"- {company}" for company in companies)

    template = Template(load_prompt("news_searcher"))

    return template.substitute(
        companies_text=companies_text,
        start_date=start_date,
        end_date=end_date,
    )
