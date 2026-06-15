"""
ai_engine.py
Multi-provider AI integration for extracting job details from job circulars.

Supported providers:
  - Claude   (Anthropic)          — anthropic SDK
  - Gemini   (Google)             — OpenAI-compatible REST
  - GPT-4o   (OpenAI)             — OpenAI-compatible REST
  - Grok     (xAI)                — OpenAI-compatible REST
  - Llama    (via Groq)           — OpenAI-compatible REST
"""

import json
import anthropic
import httpx


# ─────────────────────────────────────────────────────────────────────────────
# Custom Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class AIError(Exception):
    """Base class for all AI engine errors."""
    pass

class AIAuthenticationError(AIError):
    """Raised when an API key is invalid."""
    pass

class AINetworkError(AIError):
    """Raised when there's a connection or timeout error."""
    pass

class AIRateLimitError(AIError):
    """Raised when rate limits are exceeded."""
    pass

class AIResponseError(AIError):
    """Raised when the AI returns an invalid or incomplete response."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Provider registry  —  add / remove providers here only
# ─────────────────────────────────────────────────────────────────────────────

PROVIDERS: dict[str, dict] = {
    "claude": {
        "name":       "Claude",
        "label":      "Claude (Anthropic)",
        "emoji":      "🔷",
        "model":      "claude-sonnet-4-5",
        "config_key": "claude_api_key",
        "type":       "anthropic",
        "base_url":   None,
    },
    "gemini": {
        "name":       "Gemini",
        "label":      "Gemini (Google)",
        "emoji":      "✨",
        "model":      "gemini-2.0-flash",
        "config_key": "gemini_api_key",
        "type":       "openai_compat",
        "base_url":   "https://generativelanguage.googleapis.com/v1beta/openai",
    },
    "gpt": {
        "name":       "GPT-4o",
        "label":      "GPT-4o (OpenAI)",
        "emoji":      "🤖",
        "model":      "gpt-4o-mini",
        "config_key": "openai_api_key",
        "type":       "openai_compat",
        "base_url":   "https://api.openai.com/v1",
    },
    "grok": {
        "name":       "Grok",
        "label":      "Grok (xAI)",
        "emoji":      "⚡",
        "model":      "grok-3-mini",
        "config_key": "grok_api_key",
        "type":       "openai_compat",
        "base_url":   "https://api.x.ai/v1",
    },
    "llama": {
        "name":       "Llama",
        "label":      "Llama via Groq",
        "emoji":      "🦙",
        "model":      "llama-3.3-70b-versatile",
        "config_key": "groq_api_key",
        "type":       "openai_compat",
        "base_url":   "https://api.groq.com/openai/v1",
    },
}

# Ordered list used for UI display
PROVIDER_ORDER: list[str] = ["claude", "gemini", "gpt", "grok", "llama"]

# ─────────────────────────────────────────────────────────────────────────────
# Shared system prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a job application assistant. Extract job information from the provided job circular. "
    "Return ONLY valid JSON with these exact fields, nothing else:\n"
    '{"job_title": "", "company_name": "", "role": ""}\n\n'
    "Where:\n"
    "- job_title: A resume heading suitable for this position (e.g. 'Senior Software Engineer')\n"
    "- company_name: The employer/company name exactly as written\n"
    "- role: The actual position/role name (e.g. 'Backend Developer')\n\n"
    "Return ONLY the JSON object. No markdown fences, no explanation, no extra text."
)


# ─────────────────────────────────────────────────────────────────────────────
# AIEngine
# ─────────────────────────────────────────────────────────────────────────────

class AIEngine:
    """Handles AI interactions across multiple providers via a unified interface."""

    def __init__(self, provider_id: str, api_key: str) -> None:
        """
        Initialise the AI engine for a specific provider.

        Args:
            provider_id : One of the keys in PROVIDERS (e.g. 'claude', 'gemini').
            api_key     : API key for the chosen provider.

        Raises:
            ValueError: If provider_id is unknown or api_key is empty.
        """
        if provider_id not in PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider_id!r}. "
                f"Valid options: {list(PROVIDERS.keys())}"
            )
        if not api_key or not api_key.strip():
            raise ValueError(f"API key for '{provider_id}' cannot be empty.")

        self.provider_id: str  = provider_id
        self.provider:    dict = PROVIDERS[provider_id]
        self.api_key:     str  = api_key.strip()

        # Initialise the appropriate client
        if self.provider["type"] == "anthropic":
            self._anthropic_client = anthropic.Anthropic(api_key=self.api_key)
            self._http: httpx.Client | None = None
        else:
            self._anthropic_client = None
            self._http = httpx.Client(
                base_url=self.provider["base_url"],
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
                timeout=60.0,
            )

    # ── Public interface ──────────────────────────────────────────────────────

    def extract_job_details(self, job_circular: str) -> dict:
        """
        Send job circular text to the active AI and extract structured job details.

        Args:
            job_circular: Raw text of the job circular / job posting.

        Returns:
            dict with keys: job_title, company_name, role

        Raises:
            AIResponseError: If input is empty or the AI response JSON is invalid.
            AIError:  If the API call fails (Authentication, Network, Rate Limit).
        """
        if not job_circular or not job_circular.strip():
            raise AIResponseError("Job circular text cannot be empty.")

        user_msg = (
            "Extract job details from this job circular and return ONLY the JSON:\n\n"
            + job_circular.strip()
        )

        if self.provider["type"] == "anthropic":
            return self._call_claude(user_msg)
        else:
            return self._call_openai_compat(user_msg)

    def test_connection(self) -> tuple[bool, str]:
        """
        Send a minimal request to verify the API key and connectivity.

        Returns:
            (True, success_message) or (False, error_message)
        """
        ping = "Reply with the single word: OK"
        try:
            if self.provider["type"] == "anthropic":
                msg = self._anthropic_client.messages.create(
                    model=self.provider["model"],
                    max_tokens=20,
                    messages=[{"role": "user", "content": ping}],
                )
                reply = msg.content[0].text.strip() if msg.content else ""
            else:
                payload = {
                    "model":      self.provider["model"],
                    "max_tokens": 20,
                    "messages":   [{"role": "user", "content": ping}],
                }
                resp = self._http.post("/chat/completions", json=payload)
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"].strip()

            return True, f"{self.provider['name']} connected! Response: {reply!r}"

        except anthropic.AuthenticationError:
            return False, f"Authentication failed — invalid {self.provider['name']} API key."
        except anthropic.RateLimitError:
            return False, f"{self.provider['name']} rate limit exceeded. Please wait a moment."
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
            return False, f"Network/Timeout error — cannot reach {self.provider['name']} API: {e}"
        except anthropic.APIError as e:
            return False, f"{self.provider['name']} API error: {e}"
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            if code == 401:
                return False, f"Invalid {self.provider['name']} API key (HTTP 401)."
            elif code == 429:
                return False, f"{self.provider['name']} rate limit exceeded (HTTP 429)."
            return False, f"{self.provider['name']} HTTP {code}: {e.response.text[:120]}"
        except httpx.TimeoutException:
            return False, f"Timeout connecting to {self.provider['name']} API."
        except httpx.ConnectError:
            return False, f"Cannot connect to {self.provider['name']} API."
        except Exception as e:
            return False, f"Unexpected error: {e}"

    # ── Private helpers ───────────────────────────────────────────────────────

    def _call_claude(self, user_msg: str) -> dict:
        """Claude (Anthropic SDK) call."""
        try:
            msg = self._anthropic_client.messages.create(
                model=self.provider["model"],
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
        except anthropic.AuthenticationError:
            raise AIAuthenticationError("Invalid Claude API key. Please check Settings.")
        except anthropic.RateLimitError:
            raise AIRateLimitError("Claude rate limit exceeded. Please wait a moment before trying again.")
        except (anthropic.APIConnectionError, anthropic.APITimeoutError):
            raise AINetworkError("Cannot connect to Claude API. Check your internet connection or try again later.")
        except anthropic.APIError as e:
            raise AIError(f"Claude API error: {e}")

        if not msg.content:
            raise AIResponseError("Claude returned an empty response.")
        return self._parse_json(msg.content[0].text)

    def _call_openai_compat(self, user_msg: str) -> dict:
        """OpenAI-compatible REST call (Gemini, GPT, Grok, Groq/Llama)."""
        payload = {
            "model":      self.provider["model"],
            "max_tokens": 512,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
        }
        try:
            resp = self._http.post("/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            if code == 401:
                raise AIAuthenticationError(
                    f"Invalid {self.provider['name']} API key. Please check Settings."
                )
            elif code == 429:
                raise AIRateLimitError(
                    f"{self.provider['name']} rate limit exceeded. Please wait a moment before trying again."
                )
            else:
                raise AIError(
                    f"{self.provider['name']} API error {code}: {e.response.text[:200]}"
                )
        except httpx.TimeoutException:
            raise AINetworkError(
                f"Timeout connecting to {self.provider['name']} API. The service might be slow right now."
            )
        except httpx.ConnectError:
            raise AINetworkError(
                f"Cannot connect to {self.provider['name']} API. Check your internet connection."
            )
        except Exception as e:
            raise AIError(f"Unexpected {self.provider['name']} error: {e}")

        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_json(content)

    def _parse_json(self, text: str) -> dict:
        """Strip markdown fences and parse JSON; validate required fields."""
        text = text.strip()

        # Strip markdown code fences (```json ... ```)
        if text.startswith("```"):
            lines = text.splitlines()
            lines = lines[1:] if lines else lines
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise AIResponseError(
                f"AI returned invalid JSON.\nRaw: {text!r}\nError: {e}"
            )

        required = ["job_title", "company_name", "role"]
        missing  = [f for f in required if f not in data]
        if missing:
            raise AIResponseError(
                f"AI response missing fields: {missing}\nRaw: {text!r}"
            )

        return {k: str(data[k]).strip() for k in required}

    def __del__(self) -> None:
        """Close the httpx client if it was opened."""
        if self._http:
            try:
                self._http.close()
            except Exception:
                pass
