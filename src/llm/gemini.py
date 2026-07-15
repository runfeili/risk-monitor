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


class GeminiProvider:
    def __init__(self, models=None):
        self.models = models or GEMINI_MODELS

        self.model_index = 0

        self.key_manager = APIKeyManager(GEMINI_API_KEYS)

        self.google_search_tool = Tool(google_search=GoogleSearch())

        self._set_api_key(self.key_manager.current)

    def _set_api_key(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _run_with_retry(
        self,
        func,
        max_retry=3,
    ):

        last_exception = None

        while True:
            self._set_api_key(self.key_manager.current)

            for retry in range(max_retry + 1):
                try:
                    return func()

                except Exception as exc:
                    last_exception = exc

                    if self._is_key_error(exc):
                        logger.warning(
                            "API key exhausted (%d/%d). Reason=%s",
                            self.key_manager.current_index + 1,
                            self.key_manager.total,
                            self._error_summary(exc),
                        )
                        break

                    elif self._is_retryable_error(exc):
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

                        else:
                            break

                    else:
                        raise

            if self.key_manager.rotate():
                logger.info(
                    "Switching API key to %d/%d",
                    self.key_manager.current_index + 1,
                    self.key_manager.total,
                )
                continue
            else:
                logger.warning(
                    "All API keys exhausted for model [%s].",
                    self.current_model,
                )
                raise last_exception

    def generate(
        self,
        prompt: str,
        *,
        use_search: bool = False,
        temperature: float = 0,
    ) -> str:

        config = GenerateContentConfig(
            temperature=temperature,
        )

        if use_search:
            config.tools = [self.google_search_tool]

        last_exception = None

        while True:
            try:
                return self._run_with_retry(
                    lambda: (
                        self.client.models.generate_content(
                            model=self.current_model,
                            contents=prompt,
                            config=config,
                        ).text
                    )
                )

            except Exception as exc:
                last_exception = exc

                logger.warning(
                    "Gemini model [%s] failed: %s",
                    self.current_model,
                    self._error_summary(exc),
                )

                if self.rotate_model():
                    logger.info(
                        "Switching Gemini model from [%s] to [%s].",
                        self.models[self.model_index - 1],
                        self.current_model,
                    )
                    continue

                logger.error(
                    "All Gemini models failed. Last error: %s",
                    self._error_summary(last_exception),
                )

                raise last_exception

    @property
    def current_model(self) -> str:
        return self.models[self.model_index]

    def rotate_model(self) -> bool:
        self.model_index += 1

        if self.model_index >= len(self.models):
            self.model_index = 0
            return False

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
        msg = str(exc).lower()

        keywords = (
            "429",
            "500",
            "502",
            "503",
            "504",
            "timeout",
            "connection",
        )

        return any(k in msg for k in keywords)
