"""DataUpdateCoordinator for Loggy AI integration."""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.persistent_notification import async_create

from .const import (
    DOMAIN,
    CONF_PROVIDER,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_DAYS_TO_REVIEW,
    CONF_LOG_PATH,
    CONF_THINKING_LEVEL,
    UPDATE_INTERVAL,
    DEFAULT_DAYS_TO_REVIEW,
    DEFAULT_LOG_PATH,
    DEFAULT_THINKING_LEVEL,
    PROVIDERS,
    LOG_FILE_NOT_FOUND_MSG,
    LOG_PATHS,
)
from .utils import find_log_file

_LOGGER = logging.getLogger(__name__)

STORAGE_DIR = ".storage"
HISTORY_FILE = "loggy_ai_history.json"


class LoggyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage the Loggy AI data update process."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.config_entry = config_entry
        self.hass = hass
        self._last_analysis = None
        self._error_count = 0
        self._warning_count = 0
        self._new_issues_count = 0
        self._analysis_text = ""
        self._known_issues: List[str] = []
        self._load_issue_history()

    def _load_issue_history(self) -> None:
        """Load known issues from storage."""
        storage_path = os.path.join(
            self.hass.config.path(), STORAGE_DIR, HISTORY_FILE
        )
        try:
            if os.path.exists(storage_path):
                with open(storage_path, "r") as f:
                    data = json.load(f)
                    self._known_issues = data.get("known_issues", [])
                    _LOGGER.debug(f"Loaded {len(self._known_issues)} known issues from history")
        except Exception as err:
            _LOGGER.warning(f"Failed to load issue history: {err}")
            self._known_issues = []

    def _save_issue_history(self, issues: List[str]) -> None:
        """Save known issues to storage."""
        storage_path = os.path.join(
            self.hass.config.path(), STORAGE_DIR, HISTORY_FILE
        )
        try:
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            data = {
                "known_issues": issues,
                "last_updated": datetime.now().isoformat(),
            }
            with open(storage_path, "w") as f:
                json.dump(data, f, indent=2)
            _LOGGER.debug(f"Saved {len(issues)} known issues to history")
        except Exception as err:
            _LOGGER.error(f"Failed to save issue history: {err}")

    def _extract_issue_signature(self, log_line: str) -> str:
        """Extract a unique signature from a log line for tracking."""
        try:
            # Extract component name and first part of error message
            parts = log_line.split("]", 1)
            if len(parts) > 1:
                component = parts[0].split("[")[-1] if "[" in parts[0] else "unknown"
                message = parts[1][:100].strip()
                return f"{component}|{message}"
            return log_line[:150]
        except (IndexError, AttributeError):
            return log_line[:150]

    def _find_log_file(self, configured_path: str) -> str:
        """Find the log file by checking common locations."""
        # Build list with configured path first, then common paths
        paths_to_check = [configured_path] + [p for p in LOG_PATHS if p != configured_path]
        
        # Remove duplicates while preserving order
        unique_paths = list(dict.fromkeys(paths_to_check))
        
        # Try each path
        for path in unique_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path) and os.path.isfile(expanded_path):
                if expanded_path != os.path.expanduser(configured_path):
                    _LOGGER.info(f"Log file found at {expanded_path} (configured path {configured_path} not found)")
                return expanded_path
        
        # If no file found, raise error with all attempted paths
        checked_paths = "\n  • ".join(LOG_PATHS)
        error_msg = (
            f"Log file not found at: {configured_path}\n\n"
            f"Common locations checked:\n  • {checked_paths}\n\n"
            f"Please check Settings → Devices & Services → Loggy AI → Configure "
            f"to update the log file path."
        )
        _LOGGER.error(error_msg)
        raise UpdateFailed(error_msg)

    def _read_and_filter_logs(self) -> tuple[str, int, int]:
        """Read logs and filter by date range and severity."""
        configured_path = self.config_entry.data.get(CONF_LOG_PATH, DEFAULT_LOG_PATH)
        days_to_review = self.config_entry.data.get(
            CONF_DAYS_TO_REVIEW, DEFAULT_DAYS_TO_REVIEW
        )

        try:
            # Auto-detect log file location
            log_path = self._find_log_file(configured_path)

            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()

            cutoff_date = datetime.now() - timedelta(days=days_to_review)
            recent_lines = []
            error_count = 0
            warning_count = 0

            for line in log_content.splitlines():
                # Filter by severity
                has_error = "ERROR" in line
                has_warning = "WARNING" in line

                if not has_error and not has_warning:
                    continue

                # Try to parse date and filter
                try:
                    parts = line.split(" ")
                    if len(parts) >= 2:
                        timestamp_str = parts[0] + " " + parts[1]
                        log_date = datetime.fromisoformat(timestamp_str.split(".")[0])
                        if log_date <= cutoff_date:
                            continue
                except (ValueError, IndexError):
                    # If we can't parse date, include the line anyway
                    pass

                recent_lines.append(line)
                if has_error:
                    error_count += 1
                if has_warning:
                    warning_count += 1

            filtered_content = "\n".join(recent_lines)
            _LOGGER.info(
                f"Filtered logs: {len(recent_lines)} lines, "
                f"{error_count} errors, {warning_count} warnings"
            )
            return filtered_content, error_count, warning_count

        except Exception as err:
            _LOGGER.error(f"Failed to read log file: {err}")
            raise UpdateFailed(f"Failed to read log file: {err}")

    async def _call_gemini_api(
        self, prompt: str, api_key: str, model: str, thinking_level: str
    ) -> str:
        """Call Gemini API for analysis."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            config_dict = {
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }

            # Add thinking_level for Gemini 3.0 models only
            if "3.0" in model or "3-0" in model:
                config_dict["thinking_level"] = thinking_level

            config = types.GenerateContentConfig(**config_dict)

            response = await self.hass.async_add_executor_job(
                lambda: client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
            )

            if response and hasattr(response, "text"):
                return response.text
            else:
                raise UpdateFailed("Empty response from Gemini API")

        except Exception as err:
            _LOGGER.error(f"Gemini API error: {err}")
            raise UpdateFailed(f"Gemini API error: {err}")

    async def _call_openai_api(self, prompt: str, api_key: str, model: str) -> str:
        """Call OpenAI API for analysis."""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Home Assistant administrator skilled at analyzing logs and providing clear, actionable guidance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                raise UpdateFailed("Empty response from OpenAI API")

        except Exception as err:
            _LOGGER.error(f"OpenAI API error: {err}")
            raise UpdateFailed(f"OpenAI API error: {err}")

    async def _call_anthropic_api(self, prompt: str, api_key: str, model: str) -> str:
        """Call Anthropic API for analysis."""
        try:
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=api_key)

            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
                system="You are an expert Home Assistant administrator skilled at analyzing logs and providing clear, actionable guidance.",
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                raise UpdateFailed("Empty response from Anthropic API")

        except Exception as err:
            _LOGGER.error(f"Anthropic API error: {err}")
            raise UpdateFailed(f"Anthropic API error: {err}")

    def _build_analysis_prompt(self, log_content: str, days: int) -> str:
        """Build the AI analysis prompt."""
        return f"""You are an expert Home Assistant administrator. Analyze the following Home Assistant log content, which covers the last {days} days and contains ONLY ERROR and WARNING messages.

Your task:
1. Identify and categorize all issues by severity and component
2. Group recurring issues together
3. Provide clear, actionable recommendations for each issue
4. Explain technical jargon in plain English
5. Structure your response with:
   - 🔴 CRITICAL ISSUES (require immediate action)
   - ⚠️ WARNINGS (should be addressed soon)
   - 💡 RECOMMENDATIONS (improvements and preventive measures)

Be specific about:
- Which component or integration has the issue
- What the error means in plain language
- Exactly what to do to fix it (step-by-step if needed)
- Whether this is likely a bug, misconfiguration, or expected behavior

Keep your tone helpful, conversational, and encouraging. If an issue is common/harmless, say so!

Here is the log content:
{log_content}"""

    async def _perform_analysis(self) -> Dict[str, Any]:
        """Perform the complete log analysis."""
        _LOGGER.info("Starting log analysis")

        # Read and filter logs
        log_content, error_count, warning_count = await self.hass.async_add_executor_job(
            self._read_and_filter_logs
        )

        self._error_count = error_count
        self._warning_count = warning_count

        if not log_content.strip():
            _LOGGER.info("No errors or warnings found in logs")
            self._analysis_text = "✅ No errors or warnings found in your Home Assistant logs. Everything looks good!"
            self._new_issues_count = 0
            return {
                "last_run": datetime.now().isoformat(),
                "error_count": 0,
                "warning_count": 0,
                "new_issues_count": 0,
                "analysis_text": self._analysis_text,
            }

        # Extract issue signatures for tracking
        current_issues = []
        for line in log_content.splitlines():
            if "ERROR" in line or "WARNING" in line:
                signature = self._extract_issue_signature(line)
                if signature not in current_issues:
                    current_issues.append(signature)

        # Count new issues
        new_issues = [i for i in current_issues if i not in self._known_issues]
        self._new_issues_count = len(new_issues)
        _LOGGER.info(f"Found {len(new_issues)} new issues out of {len(current_issues)} total")

        # Update known issues
        all_known = list(set(self._known_issues + current_issues))
        self._save_issue_history(all_known)
        self._known_issues = all_known

        # Get configuration
        provider = self.config_entry.data.get(CONF_PROVIDER, "gemini")
        api_key = self.config_entry.data.get(CONF_API_KEY)
        model = self.config_entry.data.get(
            CONF_MODEL, PROVIDERS[provider]["default_model"]
        )
        days_to_review = self.config_entry.data.get(
            CONF_DAYS_TO_REVIEW, DEFAULT_DAYS_TO_REVIEW
        )
        thinking_level = self.config_entry.data.get(
            CONF_THINKING_LEVEL, DEFAULT_THINKING_LEVEL
        )

        # Build prompt
        prompt = self._build_analysis_prompt(log_content, days_to_review)

        # Call AI provider
        try:
            if provider == "gemini":
                analysis_text = await self._call_gemini_api(
                    prompt, api_key, model, thinking_level
                )
            elif provider == "openai":
                analysis_text = await self._call_openai_api(prompt, api_key, model)
            elif provider == "anthropic":
                analysis_text = await self._call_anthropic_api(prompt, api_key, model)
            else:
                raise UpdateFailed(f"Unknown provider: {provider}")

            self._analysis_text = analysis_text
            self._last_analysis = datetime.now()

            # Send notification
            await self._send_notification(analysis_text, error_count, warning_count, len(new_issues))

            _LOGGER.info("Log analysis completed successfully")

            return {
                "last_run": datetime.now().isoformat(),
                "error_count": error_count,
                "warning_count": warning_count,
                "new_issues_count": len(new_issues),
                "analysis_text": analysis_text,
            }

        except Exception as err:
            _LOGGER.error(f"Analysis failed: {err}")
            raise UpdateFailed(f"Analysis failed: {err}")

    async def _send_notification(
        self, analysis_text: str, error_count: int, warning_count: int, new_issues: int
    ) -> None:
        """Send a persistent notification with analysis results."""
        title = "🤖 Loggy AI - Log Analysis Complete"
        
        summary = f"""
**Summary:**
- 🔴 Errors: {error_count}
- ⚠️ Warnings: {warning_count}
- 🆕 New Issues: {new_issues}

---

{analysis_text}
"""

        await async_create(
            self.hass,
            summary,
            title=title,
            notification_id="loggy_ai_analysis",
        )

    async def async_request_analysis(self) -> None:
        """Request an immediate analysis (manual trigger)."""
        _LOGGER.info("Manual analysis requested")
        await self.async_request_refresh()

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the log source."""
        try:
            return await self._perform_analysis()
        except Exception as err:
            _LOGGER.error(f"Update failed: {err}")
            # Return cached data on error
            return {
                "last_run": self._last_analysis.isoformat() if self._last_analysis else None,
                "error_count": self._error_count,
                "warning_count": self._warning_count,
                "new_issues_count": self._new_issues_count,
                "analysis_text": self._analysis_text or "Analysis failed. Check logs for details.",
            }

    @property
    def error_count(self) -> int:
        """Return the error count."""
        return self._error_count

    @property
    def warning_count(self) -> int:
        """Return the warning count."""
        return self._warning_count

    @property
    def new_issues_count(self) -> int:
        """Return the new issues count."""
        return self._new_issues_count

    @property
    def analysis_text(self) -> str:
        """Return the analysis text."""
        return self._analysis_text
