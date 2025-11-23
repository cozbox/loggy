# 🤖 Loggy AI - Intelligent Log Analyzer for Home Assistant

AI-powered log analysis for Home Assistant that automatically identifies, categorizes, and explains errors and warnings in plain English with actionable solutions.

## ✨ Features

- **AI-Powered Analysis**: Uses Gemini 3.0, OpenAI, or Anthropic to analyze your logs
- **Smart Issue Tracking**: Distinguishes between new and recurring issues
- **Plain English Explanations**: Converts technical jargon into clear, actionable guidance
- **Scheduled Analysis**: Weekly automated log reviews
- **Manual Triggers**: Analyze logs on-demand via button or service
- **Rich Notifications**: Formatted persistent notifications with categorized issues
- **Multiple Sensors**: Track errors, warnings, new issues, and full analysis
- **Custom Dashboard Card**: Beautiful Lovelace card with stats and controls

## 📋 Requirements

- Home Assistant 2024.1.0 or newer
- API key from one of:
  - **Google Gemini** (recommended): https://aistudio.google.com/apikey
  - **OpenAI**: https://platform.openai.com/api-keys
  - **Anthropic**: https://console.anthropic.com/settings/keys

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/cozbox/loggy`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Loggy AI" and install
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/loggy_ai` folder to your Home Assistant's `custom_components` directory
3. Copy the `www/community/loggy-ai-card` folder to your Home Assistant's `www/community` directory
4. Restart Home Assistant

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Loggy AI"
4. Select your AI provider (Gemini, OpenAI, or Anthropic)
5. Enter your API key
6. Configure additional settings:
   - **AI Model**: Choose the specific model to use
   - **Days to Review**: How many days of logs to analyze (1-90)
   - **Log File Path**: Path to your Home Assistant log file (default: `/config/home-assistant.log`)
   - **Thinking Level**: For Gemini 3.0 models (low/medium/high)
   - **Schedule Enabled**: Enable weekly automated analysis
   - **Schedule Day**: Day of the week for automated analysis
   - **Schedule Time**: Time of day for automated analysis (HH:MM:SS)

The integration will validate your API key during setup.

### Quick Dashboard Setup (Optional but Recommended)

After configuring the integration, set up the pre-configured dashboard:

1. Download `loggy_ai_dashboard.yaml` from the repository
2. Go to **Settings** → **Dashboards** → **+ Add Dashboard**
3. Name it "Loggy AI" with icon `mdi:robot`
4. Edit the dashboard, switch to raw YAML editor
5. Paste the contents of `loggy_ai_dashboard.yaml`
6. Save and enjoy your complete Loggy AI dashboard!

See the [Dashboard Setup](#quick-start-dashboard-setup) section for detailed instructions.

### Getting API Keys

#### Google Gemini (Recommended)
1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into Loggy AI

**Recommended Model**: `gemini-3.0-pro-preview`

#### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it into Loggy AI

**Recommended Model**: `gpt-4o`

#### Anthropic Claude
1. Visit https://console.anthropic.com/settings/keys
2. Sign in or create an account
3. Click "Create Key"
4. Copy the key and paste it into Loggy AI

**Recommended Model**: `claude-3-7-sonnet-20250219`

## 📊 Sensors

After setup, the integration creates four sensors:

- **Error Count**: Number of errors found in logs
- **Warning Count**: Number of warnings found in logs
- **New Issues Count**: Number of new issues (not seen before)
- **Analysis**: Full AI analysis text with recommendations

All sensors update automatically every hour or when manually triggered.

## 🎯 Usage

### Manual Analysis

**Via Button Entity:**
Press the "Analyze Now" button entity in your dashboard or devices page.

**Via Service Call:**
```yaml
service: loggy_ai.analyze_logs
```

**Via Custom Card:**
Use the "Analyze Now" button in the Loggy AI dashboard card.

### Quick Start Dashboard Setup

Loggy AI provides multiple ways to set up the dashboard, making it work with any Home Assistant configuration:

#### 🎯 Automatic Setup (Recommended)

After installing, Loggy AI will **automatically**:
- Create a dashboard in your UI (check sidebar for "Loggy AI")
- Copy dashboard file to `config/dashboards/loggy_ai.yaml` (if folder exists)
- Auto-detect your log file location from common paths

**Just install and go!** The dashboard should appear in your sidebar.

#### 📂 Manual Setup Options

If automatic setup doesn't work, choose the option that matches your Home Assistant configuration:

**Option 1 - UI Dashboard (Storage Mode)**
1. Go to **Settings** → **Dashboards** → **+ Add Dashboard**
2. Enter title: "Loggy AI" with icon `mdi:robot`
3. Click **Create**
4. Click the three dots → **Edit Dashboard** → **Raw configuration editor**
5. Copy and paste the contents of `loggy_ai_dashboard.yaml`
6. Click **Save**

**Option 2 - Dashboards Folder**
1. Copy `dashboards/loggy_ai.yaml` to your `config/dashboards/` folder
2. Add this to your `configuration.yaml`:
   ```yaml
   lovelace:
     dashboards:
       loggy-ai:
         mode: yaml
         title: Loggy AI
         icon: mdi:robot
         show_in_sidebar: true
         filename: dashboards/loggy_ai.yaml
   ```
3. Restart Home Assistant

**Option 3 - Lovelace YAML Mode (Legacy)**
1. Copy the view from `ui-lovelace-loggy-example.yaml`
2. Add it to your `ui-lovelace.yaml` file
3. Add the custom card resource (if not already added):
   ```yaml
   lovelace:
     mode: yaml
     resources:
       - url: /local/community/loggy-ai-card/loggy-card.js
         type: module
   ```
4. Restart Home Assistant

**Option 4 - Add as a View to Existing Dashboard**
- Edit your existing dashboard
- Click **Add View**
- Switch to YAML mode
- Paste the view section from `loggy_ai_dashboard.yaml`
- Click **Save**

📚 **See `configuration.yaml.example` for complete configuration examples**

The pre-configured dashboard includes:
- Main Loggy AI custom card with statistics and analysis
- Quick action button for on-demand analysis
- Individual statistic cards for errors, warnings, and new issues
- Historical trend graph (7 days)
- Detailed analysis markdown card with full text

### Dashboard Card

To add just the custom Lovelace card to any dashboard:

1. Edit your dashboard
2. Click "Add Card"
3. Scroll down and select "Manual" or use YAML mode
4. Add this configuration:

```yaml
type: custom:loggy-card
entity: sensor.loggy_ai_log_analyzer_analysis
```

The card displays:
- Error, warning, and new issue counts
- Last analysis timestamp
- Full analysis text with color-coded sections
- "Analyze Now" button

### Automations

**Notify on High Error Count:**
```yaml
automation:
  - alias: "Alert on High Errors"
    trigger:
      - platform: numeric_state
        entity_id: sensor.loggy_ai_log_analyzer_error_count
        above: 10
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ High Error Count"
          message: "Found {{ states('sensor.loggy_ai_log_analyzer_error_count') }} errors in logs"
```

**Notify on New Issues:**
```yaml
automation:
  - alias: "Alert on New Issues"
    trigger:
      - platform: numeric_state
        entity_id: sensor.loggy_ai_log_analyzer_new_issues_count
        above: 0
    action:
      - service: notify.mobile_app
        data:
          title: "🆕 New Issues Detected"
          message: "{{ states('sensor.loggy_ai_log_analyzer_new_issues_count') }} new issues found"
```

**Daily Summary:**
```yaml
automation:
  - alias: "Daily Log Summary"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: loggy_ai.analyze_logs
      - delay: "00:05:00"
      - service: notify.mobile_app
        data:
          title: "📊 Daily Log Summary"
          message: |
            Errors: {{ states('sensor.loggy_ai_log_analyzer_error_count') }}
            Warnings: {{ states('sensor.loggy_ai_log_analyzer_warning_count') }}
            New Issues: {{ states('sensor.loggy_ai_log_analyzer_new_issues_count') }}
```

## 🔧 Advanced Configuration

### Changing Settings

After initial setup, you can modify settings:

1. Go to **Settings** → **Devices & Services**
2. Find "Loggy AI" in your integrations
3. Click "Configure"
4. Update any settings except the provider and API key
5. Click "Submit"

To change the provider or API key, you must remove and re-add the integration.

### Custom Log Paths

**🆕 Home Assistant 2025+ Compatibility:**
Loggy AI now supports **systemd journal** for reading logs! Starting with Home Assistant 2025+, logs are written only to the systemd journal (not to `/config/home-assistant.log`) to reduce disk writes on SBCs with SD cards.

**Smart Log Source Detection:**
Loggy AI automatically tries multiple log sources in this order:
1. **Systemd journal** (preferred for HA 2025+)
2. **Log file** (fallback for older installations)

This ensures 100% compatibility with both new and old Home Assistant installations!

**Loggy AI automatically detects your log file location!** It checks these common paths:
- `/config/home-assistant.log` (Docker/HA OS/Supervised)
- `~/.homeassistant/home-assistant.log` (Core)
- `/usr/share/hassio/homeassistant/home-assistant.log` (Alternative supervised)

If your log file is in a non-standard location, you can specify the full path during setup. The integration will still try to auto-detect if your specified path isn't found.

**Common locations by installation type:**
- Docker: `/config/home-assistant.log`
- Home Assistant OS: `/config/home-assistant.log`
- Supervised: `/config/home-assistant.log`
- Core: `~/.homeassistant/home-assistant.log`

**Note:** If you're running Home Assistant 2025+ on an SBC (like Raspberry Pi), your logs will be read from the systemd journal automatically, and the log file path configuration will be ignored.

### Issue History

Loggy AI tracks known issues in `.storage/loggy_ai_history.json`. This allows it to:
- Identify new vs recurring issues
- Avoid alert fatigue from known issues
- Track issue trends over time

The history file is automatically managed and doesn't require manual intervention.

## 🐛 Troubleshooting

### "Entity not found" Error
- Ensure the integration is properly installed
- Restart Home Assistant
- Check that sensors are created in Developer Tools → States

### "Invalid API Key" Error
- Verify your API key is correct
- Check that your API key has sufficient quota/credits
- Ensure you selected the correct provider

### No Errors/Warnings Found
- **Home Assistant 2025+:** Logs are read from systemd journal automatically
- **Older versions:** Check that the log file path is correct
- Verify logs are being generated (check Home Assistant logs)
- Increase "Days to Review" to capture more history
- Check Home Assistant logs for any Loggy AI errors

### Log File Not Found (Older Installations)
- **Don't worry!** Loggy AI tries systemd journal first
- If you see this on HA 2025+, it's expected (journal is being used)
- For older installations, verify the log file path in Settings → Devices & Services → Loggy AI → Configure
- Loggy AI auto-detects common log locations

### Analysis Takes Too Long
- Use a faster model (e.g., `gpt-4o-mini` or `gemini-2.5-flash-latest`)
- Reduce "Days to Review"
- Check your internet connection

### Custom Card Not Loading
- Ensure HACS is installed and updated
- Clear browser cache (Ctrl+Shift+R)
- Add the card as a custom resource in dashboard settings:
  ```
  /local/community/loggy-ai-card/loggy-card.js
  ```

## 🔒 Privacy & Security

- API keys are stored securely in Home Assistant's configuration
- Log content is sent to the selected AI provider for analysis
- No data is stored or transmitted to any other third parties
- Issue history is stored locally in `.storage/loggy_ai_history.json`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built for the Home Assistant community
- Powered by Google Gemini, OpenAI, and Anthropic AI models

## 📞 Support

- **Issues**: https://github.com/cozbox/loggy/issues
- **Discussions**: https://github.com/cozbox/loggy/discussions
- **Home Assistant Community**: https://community.home-assistant.io/

---

Made with ❤️ for Home Assistant
