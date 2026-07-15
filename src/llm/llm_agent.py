import json

from llm.gemini import GeminiProvider


class LLMAgent:
    def __init__(
        self,
        provider: str,
    ):
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

        return self.parse_json(text)

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
