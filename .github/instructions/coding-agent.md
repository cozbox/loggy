# Coding Agent Specific Instructions

applyTo: "**/*"
excludeAgent: []

## Purpose
These instructions are specifically for GitHub Copilot Coding Agent when working on code changes, bug fixes, and features in the Loggy AI Home Assistant integration.

## Critical Rules

### 1. Home Assistant Integration Constraints
- **NEVER** use synchronous/blocking operations in the main thread
- **ALWAYS** use `async`/`await` for I/O operations
- **ALWAYS** use `hass.async_add_executor_job()` for blocking calls (e.g., file I/O, API calls)
- **NEVER** import or use `time.sleep()` - use `await asyncio.sleep()` instead
- **NEVER** modify the Home Assistant event loop

### 2. Testing Requirements
Since this repository has no automated tests:
- **MUST** manually validate all changes in a Home Assistant environment
- **MUST** test config flow changes through the UI
- **MUST** verify sensor updates appear in Developer Tools → States
- **MUST** test with at least one AI provider (Gemini recommended)
- For dashboard changes, **MUST** verify rendering in Home Assistant UI

### 3. Code Changes
- **MINIMAL CHANGES ONLY**: Make the smallest possible change to fix the issue
- **PRESERVE BACKWARD COMPATIBILITY**: Don't break existing user configurations
- **FOLLOW EXISTING PATTERNS**: Match the style and structure of existing code
- **MAINTAIN CONSISTENCY**: Use patterns already established in the codebase

### 4. Configuration Safety
- **NEVER** modify existing user configurations without migration path
- **ALWAYS** provide defaults for new optional config values
- **ALWAYS** validate user inputs in config flow
- **NEVER** store secrets in plain text

### 5. Error Handling
```python
# Good - Proper error handling
try:
    result = await self._call_ai_api()
except SomeAPIError as err:
    _LOGGER.error("API call failed: %s", err)
    return "Unable to analyze logs. Please check API key and try again."
except Exception as err:
    _LOGGER.exception("Unexpected error: %s", err)
    return "An unexpected error occurred during analysis."

# Bad - No error handling
result = await self._call_ai_api()  # May crash integration!
```

### 6. Async Patterns
```python
# Good - Non-blocking file I/O
content = await self.hass.async_add_executor_job(
    self._read_log_file, log_path
)

# Bad - Blocking the event loop
with open(log_path) as f:  # DON'T DO THIS!
    content = f.read()
```

### 7. Coordinator Updates
```python
# Good - Request refresh through coordinator
await coordinator.async_request_refresh()

# Bad - Direct entity update (doesn't update coordinator state)
entity.async_write_ha_state()  # Use only when needed
```

## Common Scenarios

### Adding a New Configuration Option
1. Add constant to `const.py`
2. Add to config flow schema in `config_flow.py`
3. Add to options flow if it should be reconfigurable
4. Add translation to `strings.json`
5. Update coordinator or relevant component to use the option
6. Provide sensible default value
7. Update documentation in README.md

### Modifying AI Interaction
1. Changes go in `coordinator.py`
2. Test with all three providers if changing prompt structure
3. Handle API-specific differences (e.g., Gemini's thinking_level)
4. Add error handling for API failures
5. Consider rate limiting and quota issues
6. Log AI responses at DEBUG level for troubleshooting

### Adding/Modifying Sensors
1. Update entity class in `sensor.py`
2. Ensure coordinator provides necessary data
3. Set appropriate `device_class`, `state_class`, `unit_of_measurement`
4. Add icon if appropriate
5. Update `unique_id` generation for new sensors
6. Test entity appears in Developer Tools → States

### Dashboard/Frontend Changes
1. Update dashboard YAML in `dashboards/loggy_ai.yaml`
2. If modifying custom card: `www/community/loggy-ai-card/loggy-card.js`
3. Test in both UI mode and YAML mode Home Assistant configurations
4. Verify mobile layout
5. Ensure compatibility with different themes

## File-Specific Guidelines

### `__init__.py`
- Contains integration setup and teardown
- Registers services here
- Sets up scheduled analysis
- Handles dashboard creation
- Keep initialization logic minimal and robust

### `config_flow.py`
- UI configuration flow
- Validate ALL user inputs
- Test API keys during setup
- Provide helpful error messages
- Use `vol.Schema` for validation
- Follow Home Assistant config flow patterns

### `coordinator.py`
- Core logic for log analysis and AI calls
- Must handle all AI provider differences
- Rate limiting via UPDATE_INTERVAL
- Error recovery and fallback responses
- File I/O must be in executor
- Cache AI responses appropriately

### `sensor.py`
- Sensor entity implementations
- Link to coordinator for data
- Set proper attributes
- Handle None values gracefully
- Use appropriate state classes

### `const.py`
- All constants and configuration keys
- Provider configurations
- Default values
- Error message templates
- Keep organized and documented

## Debugging Tips

### Enable Debug Logging
Users can add to `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.loggy_ai: debug
```

### Common Issues
1. **"Entity not available"**: Coordinator update failed, check logs
2. **"API key invalid"**: Validate API key and provider match
3. **"Log file not found"**: Check file path and permissions
4. **Slow updates**: Reduce days_to_review or use faster model

### Testing Checklist
- [ ] Config flow completes successfully
- [ ] All sensors appear in UI
- [ ] Button triggers analysis
- [ ] Persistent notifications work
- [ ] Dashboard displays correctly
- [ ] No errors in Home Assistant logs
- [ ] API calls succeed with test provider
- [ ] Scheduled analysis runs (if enabled)

## Dependencies Management

### Adding New Dependencies
1. Add to `manifest.json` requirements with pinned version
2. Test installation in clean Home Assistant environment
3. Check for conflicts with Home Assistant core dependencies
4. Verify license compatibility
5. Document in README.md if user-facing

### Updating Dependencies
1. Check changelog for breaking changes
2. Update version in `manifest.json`
3. Test thoroughly with updated version
4. Update code if API changed
5. Document in RELEASE_NOTES.md

## API Provider Specific Notes

### Google Gemini
- Uses `google.genai` library
- Supports extended thinking with `thinking_level`
- Has specific model naming (gemini-2.5-pro, gemini-3.0-pro-preview)
- Rate limits vary by API key type (free vs paid)

### OpenAI
- Uses `openai` library v1.54.0
- Standard chat completions API
- Supports o1-preview (reasoning model)
- Token-based pricing model

### Anthropic
- Uses `anthropic` library v0.39.0
- Claude 3.7 Sonnet supports extended thinking
- Requires specific message format
- Context window considerations

## Performance Considerations

1. **Log File Size**: Large logs (>10MB) may slow analysis
2. **Days to Review**: More days = more content = slower analysis
3. **AI Model Speed**: Flash models faster than pro/extended models
4. **Update Frequency**: Default 1 hour, don't reduce unnecessarily
5. **Concurrent Requests**: Only one analysis at a time to avoid rate limits

## User Experience Guidelines

1. **Progressive Enhancement**: Core features work without optional config
2. **Helpful Defaults**: Sensible defaults for all optional settings
3. **Clear Error Messages**: Tell users what went wrong AND how to fix it
4. **Responsive Feedback**: Show progress for long-running operations
5. **Documentation**: Update README.md for any user-facing changes

## Git Commit Guidelines

- Clear, descriptive commit messages
- Reference issue numbers when applicable
- Group related changes in single commit
- Don't commit test data or API keys
- Follow conventional commit format when possible:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation changes
  - `refactor:` code refactoring
  - `test:` test updates
  - `chore:` maintenance tasks

## Security Checklist

- [ ] No API keys or secrets in code
- [ ] User inputs validated
- [ ] File paths validated (no path traversal)
- [ ] Error messages don't leak sensitive info
- [ ] External API calls handled securely
- [ ] Use Home Assistant's secure storage for secrets

## Common Mistakes to Avoid

1. ❌ Blocking the event loop with sync operations
2. ❌ Not handling API failures gracefully
3. ❌ Breaking existing user configurations
4. ❌ Forgetting to update strings.json for new UI text
5. ❌ Not testing with actual Home Assistant instance
6. ❌ Hardcoding values instead of using constants
7. ❌ Not providing backwards compatibility
8. ❌ Ignoring Home Assistant coding standards
9. ❌ Making changes without updating documentation
10. ❌ Not considering multi-language support

## Final Reminders

- **READ THE ERROR**: Home Assistant logs are verbose - they'll tell you what's wrong
- **TEST INCREMENTALLY**: Don't make many changes at once
- **FOLLOW PATTERNS**: Look at existing code for examples
- **ASYNC EVERYTHING**: Home Assistant is async-first
- **USER FIRST**: Think about the user experience
- **MINIMAL CHANGES**: Smallest change that fixes the issue
- **DOCUMENT**: Update relevant docs for user-facing changes

When in doubt, look at how Home Assistant core integrations handle similar scenarios. The Home Assistant developers documentation (https://developers.home-assistant.io/) is your friend.
