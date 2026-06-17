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
    "groq": {
        "name":       "Groq",
        "label":      "Groq",
        "emoji":      "🚀",
        "model":      "llama-3.3-70b-versatile",
        "config_key": "groq_api_key",
        "type":       "openai_compat",
        "base_url":   "https://api.groq.com/openai/v1",
    }
}

# Ordered list used for UI display
PROVIDER_ORDER: list[str] = ["claude", "gemini", "gpt", "grok", "llama", "groq"]

# ─────────────────────────────────────────────────────────────────────────────
# Shared system prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a job application assistant. Extract job information from the provided job circular. "
    "The circular may be in English, Bengali, or use short forms. Always output professional English values.\n"
    "Return ONLY valid JSON with these exact fields, nothing else:\n"
    '{"job_title": "", "company_name": "", "role": "", "location": "", "tech_stack": ""}\n\n'
    "Where:\n"
    "- job_title: The professional English job title exactly as the employer wants it (e.g. 'Full Stack Developer', "
    "'Frontend Developer', 'Backend Engineer', 'Product Manager'). Mirror the employer's wording precisely. "
    "If missing, use 'Software Developer'.\n"
    "- company_name: The employer/company name (translate to English if needed). If missing, use 'your company'.\n"
    "- role: Same as job_title (the exact position being applied for).\n"
    "- location: The job location. If missing, use ''.\n"
    "- tech_stack: A short list (2–4 items) of the most important technologies/skills the job requires, "
    "separated by ' · ' (space-dot-space). Choose the most recognisable ones from the circular "
    "(e.g. 'Next.js · Node.js · PostgreSQL' or 'React · TypeScript · REST APIs'). "
    "If no specific tech is mentioned, derive sensible defaults from the role "
    "(e.g. for Frontend Developer: 'React · TypeScript · CSS'). Never leave empty.\n\n"
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
            dict with keys: job_title, company_name, role, location, tech_stack

        Raises:
            AIResponseError: If input is empty or the AI response JSON is invalid.
            AIError:  If the API call fails (Authentication, Network, Rate Limit).
        """
        # Validate input
        if not job_circular or not job_circular.strip():
            raise AIResponseError("Please paste a job circular/posting to analyze.")
        
        if len(job_circular.strip()) < 20:
            raise AIResponseError("Job posting is too short. Please paste a complete job description.")

        user_msg = (
            "Extract job details from this job circular and return ONLY the JSON:\n\n"
            + job_circular.strip()
        )

        # Call appropriate provider with retry logic for transient failures
        retries = 3
        last_error = None
        
        for attempt in range(retries):
            try:
                if self.provider["type"] == "anthropic":
                    return self._call_claude(user_msg)
                else:
                    return self._call_openai_compat(user_msg)
            except (AINetworkError, AIRateLimitError) as e:
                last_error = e
                if attempt < retries - 1:
                    import time
                    time.sleep(1 + attempt)  # Exponential backoff
                    continue
            except AIAuthenticationError:
                raise  # Don't retry auth errors
        
        raise last_error or AIError("Failed after retries")

    def extract_skills(self, job_circular: str) -> list[str]:
        """
        Extract all technical skills and technologies from a job circular.

        Args:
            job_circular: Raw text of the job circular / job posting.

        Returns:
            List of skill names (e.g. ["React", "Node.js", "MongoDB"])

        Raises:
            AIResponseError: If input is empty or the AI response JSON is invalid.
            AIError:  If the API call fails.
        """
        if not job_circular or not job_circular.strip():
            raise AIResponseError("Job posting cannot be empty.")
        
        if len(job_circular.strip()) < 20:
            return []  # Return empty list for very short postings

        skills_prompt = (
            "You are a skills extraction expert. Extract ALL technical skills, "
            "programming languages, frameworks, tools, databases, and technologies "
            "mentioned in this job circular.\n\n"
            "Return ONLY a valid JSON array with skill names, nothing else:\n"
            '["Skill1", "Skill2", "Skill3"]\n\n'
            "Guidelines:\n"
            "- Include programming languages: JavaScript, Python, Java, etc.\n"
            "- Include frameworks: React, Vue.js, Django, Spring Boot, etc.\n"
            "- Include databases: MongoDB, PostgreSQL, MySQL, etc.\n"
            "- Include tools: Docker, Git, AWS, Jenkins, etc.\n"
            "- Do NOT include soft skills (communication, leadership, etc)\n"
            "- Remove duplicates\n"
            "- Each skill should be properly capitalized\n\n"
            "Job Circular:\n" + job_circular.strip()
        )

        user_msg = skills_prompt

        if self.provider["type"] == "anthropic":
            response = self._call_claude_skills(user_msg)
        else:
            response = self._call_openai_compat_skills(user_msg)

        return response

    def _call_claude_skills(self, user_msg: str) -> list[str]:
        """Claude call for skills extraction - returns list instead of dict."""
        try:
            msg = self._anthropic_client.messages.create(
                model=self.provider["model"],
                max_tokens=1024,
                messages=[{"role": "user", "content": user_msg}],
            )
        except anthropic.AuthenticationError:
            raise AIAuthenticationError("Invalid Claude API key.")
        except anthropic.RateLimitError:
            raise AIRateLimitError("Claude rate limit exceeded.")
        except (anthropic.APIConnectionError, anthropic.APITimeoutError):
            raise AINetworkError("Cannot connect to Claude API.")
        except anthropic.APIError as e:
            raise AIError(f"Claude API error: {e}")

        if not msg.content:
            raise AIResponseError("Claude returned an empty response.")
        return self._parse_skills_json(msg.content[0].text)

    def _call_openai_compat_skills(self, user_msg: str) -> list[str]:
        """OpenAI-compatible call for skills extraction - returns list."""
        payload = {
            "model":      self.provider["model"],
            "max_tokens": 1024,
            "messages":   [{"role": "user", "content": user_msg}],
        }
        try:
            resp = self._http.post("/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            if code == 401:
                raise AIAuthenticationError(f"Invalid {self.provider['name']} API key.")
            elif code == 429:
                raise AIRateLimitError(f"{self.provider['name']} rate limit exceeded.")
            else:
                raise AIError(f"{self.provider['name']} API error {code}.")
        except (httpx.TimeoutException, httpx.ConnectError):
            raise AINetworkError(f"Cannot connect to {self.provider['name']} API.")
        except Exception as e:
            raise AIError(f"Unexpected error: {e}")

        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_skills_json(content)

    def _parse_skills_json(self, text: str) -> list[str]:
        """
        Parse JSON array of skills from response.
        
        Handles markdown code fences and malformed JSON gracefully.
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()

        # Strip markdown code fences
        if text.startswith("```"):
            lines = text.splitlines()
            lines = lines[1:] if lines else lines
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise AIResponseError(f"Invalid JSON response: {e}")

        if not isinstance(data, list):
            raise AIResponseError(f"Expected JSON array, got {type(data).__name__}")

        # Clean and deduplicate
        skills = []
        seen = set()
        for skill in data:
            s = str(skill).strip()
            if s and s.lower() not in {x.lower() for x in seen}:
                skills.append(s)
                seen.add(s.lower())

        return skills

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

    def _parse_json(self, text: str, expected_keys: set[str] | None = None) -> dict:
        """
        Parse JSON from response with validation.
        
        Args:
            text: Raw response text (may contain markdown fences)
            expected_keys: Set of required keys to validate
        
        Returns:
            Parsed dict with defaults for missing fields
        
        Raises:
            AIResponseError: If JSON is malformed or missing critical fields
        """
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

        required = ["job_title", "company_name", "role", "location", "tech_stack"]
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
