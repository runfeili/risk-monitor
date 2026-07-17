import logging
import time
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    Tool,
)
from configs import GEMINI_MODELS, GEMINI_API_KEYS
from llm.api_key import APIKeyManager

logger = logging.getLogger(__name__)


class EmptyResponseError(RuntimeError):
    """Gemini returned an empty response text."""

    pass


class GeminiProvider:
    def __init__(self, models=None):

        self.usage_stats = {
            "searcher": {
                "requests": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "thoughts_tokens": 0,
                "tool_tokens": 0,
                "total_tokens": 0,
            },
            "classifier": {
                "requests": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "thoughts_tokens": 0,
                "tool_tokens": 0,
                "total_tokens": 0,
            },
        }

        self.models = models or GEMINI_MODELS
        self.model_index = 0

        self.key_manager = APIKeyManager(GEMINI_API_KEYS)
        self._set_api_key(self.key_manager.current)

        self.google_search_tool = Tool(google_search=GoogleSearch())

    def _set_api_key(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _run_with_retry(
        self,
        func,
        max_retry=3,
    ):

        for retry in range(max_retry + 1):
            try:
                return func()

            except Exception as exc:
                last_exception = exc

                if self._is_key_error(exc):
                    raise

                if self._is_retryable_error(exc):
                    if retry < max_retry:
                        wait = min(60, 2**retry)

                        logger.warning(
                            "Temporary error, retry %d/%d after %ds. Model=%s, Error=%s",
                            retry + 1,
                            max_retry,
                            wait,
                            self.current_model,
                            self._error_summary(exc),
                        )

                        time.sleep(wait)
                        continue

                raise

        raise last_exception

    def generate(
        self,
        prompt: str,
        *,
        use_search: bool = False,
        usage_tag: str = "default",
        temperature: float = 0,
    ) -> str:

        config = GenerateContentConfig(
            temperature=temperature,
        )

        if use_search:
            config.tools = [self.google_search_tool]

        self.key_manager.reset()

        last_exception = None

        while True:
            self._set_api_key(self.key_manager.current)

            self.model_index = 0

            while True:
                try:
                    response = self._run_with_retry(
                        lambda: self._generate_once(prompt, config)
                    )

                    usage = getattr(response, "usage_metadata", None)
                    if usage:
                        stats = self.usage_stats[usage_tag]
                        stats["requests"] += 1
                        stats["prompt_tokens"] += usage.prompt_token_count or 0
                        stats["output_tokens"] += usage.candidates_token_count or 0
                        stats["thoughts_tokens"] += usage.thoughts_token_count or 0
                        stats["tool_tokens"] += usage.tool_use_prompt_token_count or 0
                        stats["total_tokens"] += usage.total_token_count or 0

                        logger.info(
                            "Gemini usage | input=%d think=%d total=%d",
                            usage.prompt_token_count or 0,
                            usage.thoughts_token_count or 0,
                            usage.total_token_count or 0,
                        )

                    return response.text

                except Exception as exc:
                    last_exception = exc

                    logger.warning(
                        "Gemini model [%s] failed: %s",
                        self.current_model,
                        self._error_summary(exc),
                    )

                    if self._is_key_error(exc):
                        logger.warning(
                            "API key (%d/%d) exhausted for current model [%s].",
                            self.key_manager.current_index + 1,
                            self.key_manager.total,
                            self.current_model,
                        )
                        # break

                    if self.rotate_model():
                        logger.info(
                            "Switching model to [%s].",
                            self.current_model,
                        )
                        continue

                    logger.warning(
                        "All models failed for current API key (%d/%d).",
                        self.key_manager.current_index + 1,
                        self.key_manager.total,
                    )
                    break

            if not self.key_manager.rotate():
                break

            logger.info(
                "Switching API key to %d/%d",
                self.key_manager.current_index + 1,
                self.key_manager.total,
            )

        logger.error(
            "All Gemini API keys and models failed. Last error: %s",
            self._error_summary(last_exception),
        )
        raise last_exception

    def _generate_once(self, prompt, config):
        response = self.client.models.generate_content(
            model=self.current_model,
            contents=prompt,
            config=config,
        )

        if not response.text:
            logger.warning("Gemini returned empty response.")
            logger.error("Response: %r", response)
            raise EmptyResponseError()

        return response

    @property
    def current_model(self) -> str:
        return self.models[self.model_index]

    def rotate_model(self) -> bool:
        if self.model_index + 1 >= len(self.models):
            return False

        self.model_index += 1
        return True

    @staticmethod
    def _error_summary(exc: Exception) -> str:
        code = getattr(exc, "code", None)
        message = getattr(exc, "message", None)

        if code and message:
            return f"{code} {message.split('.')[0]}"

        return exc.__class__.__name__

    @staticmethod
    def _is_key_error(exc: Exception) -> bool:
        msg = str(exc).lower()

        keywords = (
            "invalid api key",
            "api key not valid",
            "unauthorized",
            "permission denied",
            "quota exceeded",
            "resource exhausted",
            "429",
        )

        return any(k in msg for k in keywords)

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        if isinstance(exc, EmptyResponseError):
            return True

        msg = str(exc).lower()

        keywords = (
            "500",
            "502",
            "503",
            "504",
            "timeout",
            "connection",
        )

        return any(k in msg for k in keywords)
