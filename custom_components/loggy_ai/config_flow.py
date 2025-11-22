"""Config flow for Loggy AI integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_PROVIDER,
    CONF_MODEL,
    CONF_DAYS_TO_REVIEW,
    CONF_LOG_PATH,
    CONF_THINKING_LEVEL,
    CONF_SCHEDULE_ENABLED,
    CONF_SCHEDULE_DAY,
    CONF_SCHEDULE_TIME,
    DEFAULT_DAYS_TO_REVIEW,
    DEFAULT_LOG_PATH,
    DEFAULT_THINKING_LEVEL,
    DEFAULT_SCHEDULE_DAY,
    DEFAULT_SCHEDULE_TIME,
    DEFAULT_PROVIDER,
    PROVIDERS,
    THINKING_LEVELS,
    DAYS_OF_WEEK,
)

_LOGGER = logging.getLogger(__name__)


class LoggyAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loggy AI."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate API key
            provider = user_input[CONF_PROVIDER]
            api_key = user_input[CONF_API_KEY]
            model = user_input.get(CONF_MODEL, PROVIDERS[provider]["default_model"])

            is_valid, error_msg = await self._validate_api_key(provider, api_key, model)

            if is_valid:
                # Create unique ID based on provider and partial API key
                await self.async_set_unique_id(f"{provider}_{api_key[-8:]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Loggy AI ({PROVIDERS[provider]['name']})",
                    data=user_input,
                )
            else:
                errors["base"] = error_msg or "invalid_api_key"

        # Get available models for default provider
        default_provider = DEFAULT_PROVIDER
        available_models = PROVIDERS[default_provider]["models"]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER, default=default_provider): vol.In(
                    {k: v["name"] for k, v in PROVIDERS.items()}
                ),
                vol.Required(CONF_API_KEY): str,
                vol.Optional(
                    CONF_MODEL, default=PROVIDERS[default_provider]["default_model"]
                ): vol.In(available_models),
                vol.Optional(
                    CONF_DAYS_TO_REVIEW, default=DEFAULT_DAYS_TO_REVIEW
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=90)),
                vol.Optional(CONF_LOG_PATH, default=DEFAULT_LOG_PATH): str,
                vol.Optional(
                    CONF_THINKING_LEVEL, default=DEFAULT_THINKING_LEVEL
                ): vol.In(THINKING_LEVELS),
                vol.Optional(CONF_SCHEDULE_ENABLED, default=False): bool,
                vol.Optional(
                    CONF_SCHEDULE_DAY, default=DEFAULT_SCHEDULE_DAY
                ): vol.In(DAYS_OF_WEEK),
                vol.Optional(CONF_SCHEDULE_TIME, default=DEFAULT_SCHEDULE_TIME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/cozbox/loggy"
            },
        )

    async def _validate_api_key(
        self, provider: str, api_key: str, model: str
    ) -> tuple[bool, str]:
        """Validate the API key with the provider."""
        try:
            if provider == "gemini":
                return await self._validate_gemini_key(api_key, model)
            elif provider == "openai":
                return await self._validate_openai_key(api_key, model)
            elif provider == "anthropic":
                return await self._validate_anthropic_key(api_key, model)
            else:
                return False, "unknown_provider"
        except Exception as err:
            _LOGGER.error(f"API validation error: {err}")
            return False, "validation_error"

    async def _validate_gemini_key(self, api_key: str, model: str) -> tuple[bool, str]:
        """Validate Gemini API key."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(model_name=model)

            # Make a simple test call
            response = await self.hass.async_add_executor_job(
                model_instance.generate_content, "Hello"
            )

            if response and hasattr(response, "text"):
                return True, ""
            else:
                return False, "invalid_response"

        except Exception as err:
            _LOGGER.error(f"Gemini validation error: {err}")
            if "API_KEY_INVALID" in str(err) or "INVALID_ARGUMENT" in str(err):
                return False, "invalid_api_key"
            return False, "connection_error"

    async def _validate_openai_key(self, api_key: str, model: str) -> tuple[bool, str]:
        """Validate OpenAI API key."""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)

            # Make a simple test call
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            if response.choices:
                return True, ""
            else:
                return False, "invalid_response"

        except Exception as err:
            _LOGGER.error(f"OpenAI validation error: {err}")
            if "invalid" in str(err).lower() or "unauthorized" in str(err).lower():
                return False, "invalid_api_key"
            return False, "connection_error"

    async def _validate_anthropic_key(
        self, api_key: str, model: str
    ) -> tuple[bool, str]:
        """Validate Anthropic API key."""
        try:
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=api_key)

            # Make a simple test call
            response = await client.messages.create(
                model=model,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}],
            )

            if response.content:
                return True, ""
            else:
                return False, "invalid_response"

        except Exception as err:
            _LOGGER.error(f"Anthropic validation error: {err}")
            if "invalid" in str(err).lower() or "unauthorized" in str(err).lower():
                return False, "invalid_api_key"
            return False, "connection_error"

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return LoggyAIOptionsFlow(config_entry)


class LoggyAIOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Loggy AI."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        provider = self.config_entry.data.get(CONF_PROVIDER, DEFAULT_PROVIDER)
        available_models = PROVIDERS[provider]["models"]

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MODEL,
                    default=self.config_entry.data.get(
                        CONF_MODEL, PROVIDERS[provider]["default_model"]
                    ),
                ): vol.In(available_models),
                vol.Optional(
                    CONF_DAYS_TO_REVIEW,
                    default=self.config_entry.data.get(
                        CONF_DAYS_TO_REVIEW, DEFAULT_DAYS_TO_REVIEW
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=90)),
                vol.Optional(
                    CONF_LOG_PATH,
                    default=self.config_entry.data.get(CONF_LOG_PATH, DEFAULT_LOG_PATH),
                ): str,
                vol.Optional(
                    CONF_THINKING_LEVEL,
                    default=self.config_entry.data.get(
                        CONF_THINKING_LEVEL, DEFAULT_THINKING_LEVEL
                    ),
                ): vol.In(THINKING_LEVELS),
                vol.Optional(
                    CONF_SCHEDULE_ENABLED,
                    default=self.config_entry.data.get(CONF_SCHEDULE_ENABLED, False),
                ): bool,
                vol.Optional(
                    CONF_SCHEDULE_DAY,
                    default=self.config_entry.data.get(
                        CONF_SCHEDULE_DAY, DEFAULT_SCHEDULE_DAY
                    ),
                ): vol.In(DAYS_OF_WEEK),
                vol.Optional(
                    CONF_SCHEDULE_TIME,
                    default=self.config_entry.data.get(
                        CONF_SCHEDULE_TIME, DEFAULT_SCHEDULE_TIME
                    ),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
