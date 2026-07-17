import json
import logging
from llm.gemini import GeminiProvider

logger = logging.getLogger(__name__)


class LLMAgent:
    def __init__(
        self,
        provider: str,
        usage_tag:str,
    ):
        self.usage_tag = usage_tag
        if provider == "gemini":
            self.provider = GeminiProvider()

        else:
            raise NotImplementedError

    def generate(
        self,
        prompt: str,
        *,
        use_search=False,
        temperature=0,
    ):

        return self.provider.generate(
            prompt,
            use_search=use_search,
            usage_tag=self.usage_tag,
            temperature=temperature,
        )

    def generate_json(
        self,
        prompt: str,
        **kwargs,
    ):

        text = self.generate(
            prompt,
            **kwargs,
        )

        try:
            return self.parse_json(text)
        except Exception as e:
            logger.error(f"JSON parsing failed. {e}")
            logger.error("Original response:\n%s", text)
            raise

    @staticmethod
    def parse_json(text: str):

        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        return json.loads(text)
