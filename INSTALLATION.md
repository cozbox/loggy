# 📦 Loggy AI Installation Guide

Complete step-by-step installation guide for Loggy AI - Intelligent Log Analyzer for Home Assistant.

## Prerequisites

Before installing Loggy AI, ensure you have:

- ✅ Home Assistant 2024.1.0 or newer
- ✅ HACS (Home Assistant Community Store) installed (recommended)
- ✅ An API key from Google Gemini, OpenAI, or Anthropic

## Installation Methods

### Method 1: HACS Installation (Recommended)

HACS makes installation and updates much easier.

#### Step 1: Add Custom Repository

1. Open Home Assistant
2. Navigate to **HACS** in the sidebar
3. Click on **Integrations**
4. Click the **three dots** (⋮) in the top right corner
5. Select **Custom repositories**
6. In the dialog that opens:
   - **Repository**: Enter `https://github.com/cozbox/loggy`
   - **Category**: Select `Integration`
7. Click **Add**

#### Step 2: Install Loggy AI

1. In HACS, search for **"Loggy AI"**
2. Click on the **Loggy AI** integration
3. Click **Download**
4. Select the latest version
5. Click **Download** again to confirm

#### Step 3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** in the top right
3. Click **Restart Home Assistant**
4. Wait for Home Assistant to restart (this may take a few minutes)

### Method 2: Manual Installation

If you prefer not to use HACS, you can install manually.

#### Step 1: Download Files

1. Visit https://github.com/cozbox/loggy/releases
2. Download the latest release ZIP file
3. Extract the ZIP file on your computer

#### Step 2: Copy Integration Files

1. Locate your Home Assistant configuration directory
   - Docker: `/config/`
   - Home Assistant OS: `/config/`
   - Supervised: `/usr/share/hassio/homeassistant/`
   - Core: `~/.homeassistant/`

2. Create the custom components directory if it doesn't exist:
   ```
   mkdir -p custom_components
   ```

3. Copy the `custom_components/loggy_ai` folder from the extracted ZIP to your `custom_components` directory

4. Your directory structure should look like:
   ```
   config/
   ├── custom_components/
   │   └── loggy_ai/
   │       ├── __init__.py
   │       ├── button.py
   │       ├── config_flow.py
   │       ├── const.py
   │       ├── coordinator.py
   │       ├── manifest.json
   │       ├── sensor.py
   │       ├── services.yaml
   │       ├── strings.json
   │       └── translations/
   │           └── en.json
   └── ...
   ```

#### Step 3: Copy Dashboard Card Files

1. Create the www directory structure if it doesn't exist:
   ```
   mkdir -p www/community/loggy-ai-card
   ```

2. Copy `www/community/loggy-ai-card/loggy-card.js` from the extracted ZIP to your `www/community/loggy-ai-card/` directory

#### Step 4: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** in the top right
3. Click **Restart Home Assistant**
4. Wait for Home Assistant to restart

## Configuration

### Step 1: Get an API Key

Choose one AI provider and get an API key:

#### Option A: Google Gemini (Recommended)

1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Select a project or create a new one
5. Copy the API key and save it securely

**Free Tier**: 15 requests per minute, 1,500 requests per day

#### Option B: OpenAI

1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **Create new secret key**
4. Give it a name (e.g., "Loggy AI")
5. Copy the API key and save it securely

**Pricing**: Pay-as-you-go (GPT-4o: ~$0.005 per analysis)

#### Option C: Anthropic Claude

1. Visit https://console.anthropic.com/settings/keys
2. Sign in or create an account
3. Click **Create Key**
4. Give it a name (e.g., "Loggy AI")
5. Copy the API key and save it securely

**Pricing**: Pay-as-you-go (Claude 3.7: ~$0.01 per analysis)

### Step 2: Add the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for **"Loggy AI"**
4. Click on **Loggy AI - Intelligent Log Analyzer**

### Step 3: Configure Settings

Fill out the configuration form:

#### Required Settings:

- **AI Provider**: Select `Google Gemini 3.0`, `OpenAI`, or `Anthropic Claude`
- **API Key**: Paste the API key you obtained earlier

#### Optional Settings:

- **AI Model**: 
  - Gemini: `gemini-3.0-pro-preview` (default) or `gemini-2.5-flash-latest`
  - OpenAI: `gpt-4o` (default), `gpt-4o-mini`, or `o1-preview`
  - Anthropic: `claude-3-7-sonnet-20250219` (default) or `claude-3-5-sonnet-20241022`

- **Days to Review**: Number of days of logs to analyze (1-90, default: 14)

- **Log File Path**: Path to your Home Assistant log file (default: `/config/home-assistant.log`)

- **Thinking Level**: For Gemini 3.0 models only (low/medium/high, default: high)

- **Enable Scheduled Analysis**: Check to enable weekly automated analysis

- **Schedule Day**: Day of the week for scheduled analysis (default: Sunday)

- **Schedule Time**: Time of day for scheduled analysis in HH:MM:SS format (default: 22:00:00)

### Step 4: Verify Setup

1. The integration will validate your API key
2. If successful, you'll see a success message
3. The integration will create these entities:
   - `sensor.loggy_ai_log_analyzer_error_count`
   - `sensor.loggy_ai_log_analyzer_warning_count`
   - `sensor.loggy_ai_log_analyzer_new_issues_count`
   - `sensor.loggy_ai_log_analyzer_analysis`
   - `button.loggy_ai_log_analyzer_analyze_now`

4. Check **Developer Tools** → **States** to verify the entities exist

## Dashboard Setup

### 🎯 Automatic Setup (Recommended)

After installation, Loggy AI **automatically creates the dashboard for you!**

**What happens automatically:**
- ✅ Dashboard created in your UI (check sidebar for "Loggy AI")
- ✅ Dashboard file copied to `config/dashboards/loggy_ai.yaml` (if folder exists)
- ✅ Log file location auto-detected from common paths
- ✅ Welcome notification with setup instructions

**No manual setup needed!** Just look for "Loggy AI" in your sidebar after installation.

### 📂 Manual Setup Options

If automatic setup doesn't work or you want to customize, choose the option that matches your setup:

#### Option 1: UI Dashboard (Storage Mode)

1. **Download the dashboard file:**
   - Get `loggy_ai_dashboard.yaml` from the [GitHub repository](https://github.com/cozbox/loggy)

2. **Create the dashboard in Home Assistant:**
   - Go to **Settings** → **Dashboards**
   - Click **+ Add Dashboard**
   - Enter:
     - **Title**: `Loggy AI`
     - **Icon**: `mdi:robot`
     - **URL**: `loggy-ai` (or leave default)
   - Click **Create**

3. **Import the configuration:**
   - Click the **three dots** (⋮) on the new Loggy AI dashboard
   - Select **Edit Dashboard**
   - Click the **three dots** again
   - Select **Raw configuration editor**
   - Copy and paste the entire contents of `loggy_ai_dashboard.yaml`
   - Click **Save**

#### Option 2: Dashboards Folder

1. **Copy the file:**
   - Copy `dashboards/loggy_ai.yaml` from the repository to your `config/dashboards/` folder

2. **Add to configuration.yaml:**
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

3. **Restart Home Assistant**

#### Option 3: Lovelace YAML Mode (Legacy)

1. **Copy the view:**
   - Copy the view content from `ui-lovelace-loggy-example.yaml`

2. **Add to ui-lovelace.yaml:**
   - Paste the view into your existing `ui-lovelace.yaml` file

3. **Add the custom card resource:**
   ```yaml
   lovelace:
     mode: yaml
     resources:
       - url: /local/community/loggy-ai-card/loggy-card.js
         type: module
   ```

4. **Restart Home Assistant**

📚 **See `configuration.yaml.example` in the repository for complete configuration examples for all options.**

The pre-configured dashboard includes:
- 📊 Main Loggy AI card with all statistics
- 🎯 Quick action button
- 📈 Individual statistic cards
- 📉 7-day historical trend graph
- 📝 Full analysis details

### Manual Card Setup

If you prefer to add just the card to an existing dashboard:

#### Step 1: Add the Custom Card Resource

1. Go to **Settings** → **Dashboards**
2. Click the **three dots** (⋮) in the top right
3. Select **Resources**
4. Click **+ Add Resource**
5. Enter:
   - **URL**: `/local/community/loggy-ai-card/loggy-card.js`
   - **Resource type**: `JavaScript Module`
6. Click **Create**

#### Step 2: Add the Card to Your Dashboard

1. Open the dashboard where you want to add the card
2. Click **Edit Dashboard** (pencil icon)
3. Click **+ Add Card**
4. Scroll down and click **Manual** or switch to YAML mode
5. Paste this configuration:

```yaml
type: custom:loggy-card
entity: sensor.loggy_ai_log_analyzer_analysis
```

6. Click **Save**
7. Click **Done** to exit edit mode

You should now see the Loggy AI card with stats and controls!

## First Analysis

Trigger your first analysis to test the setup:

### Option 1: Using the Button Entity

1. Go to **Settings** → **Devices & Services** → **Devices**
2. Find and click **Loggy AI Log Analyzer**
3. Click the **Analyze Now** button
4. Wait a few moments for the analysis to complete

### Option 2: Using the Dashboard Card

1. Find the Loggy AI card in your dashboard
2. Click the **▶️ Analyze Now** button
3. Wait for the analysis (button will show "⏳ Analyzing...")

### Option 3: Using a Service Call

1. Go to **Developer Tools** → **Services**
2. Select service: `loggy_ai.analyze_logs`
3. Click **Call Service**

### What to Expect

- The analysis takes 10-60 seconds depending on log size and model
- A persistent notification will appear with the results
- All sensors will update with new data
- The dashboard card will show the analysis

## Verification Checklist

✅ Integration appears in Settings → Devices & Services
✅ Four sensors and one button entity are created
✅ Dashboard card displays correctly
✅ First analysis completes successfully
✅ Persistent notification appears with results
✅ Sensors show updated values

## Next Steps

- Set up automations to get notified of issues
- Configure scheduled analysis for weekly reports
- Customize the dashboard card layout
- Adjust settings in the integration's Configure menu

## Troubleshooting

### Integration Not Found
- Clear browser cache (Ctrl+Shift+R)
- Restart Home Assistant again
- Check the logs for errors

### Invalid API Key Error
- Verify you copied the entire API key
- Check for extra spaces at the beginning or end
- Ensure the API key is active and has quota

### Custom Card Not Loading
- Verify the JavaScript file is in the correct location
- Add the resource in dashboard settings
- Clear browser cache
- Check browser console for errors (F12)

### No Entities Created
- Check Home Assistant logs for errors
- Verify the custom_components/loggy_ai folder has all required files
- Restart Home Assistant again

### Analysis Fails
- **Log file not found**: Loggy AI automatically checks multiple common locations. If still failing, manually check your log file path in Settings → Devices & Services → Loggy AI → Configure
- **Common log locations**:
  - Docker/HA OS/Supervised: `/config/home-assistant.log`
  - Core: `~/.homeassistant/home-assistant.log`
  - Alternative: `/usr/share/hassio/homeassistant/home-assistant.log`
- Verify log file is readable (check file permissions)
- Check API provider status
- Review Home Assistant logs for specific errors

### Dashboard Not Appearing
- **Storage mode**: Dashboard should auto-create - check your sidebar for "Loggy AI"
- **Dashboards folder**: Verify file copied to `config/dashboards/loggy_ai.yaml` and configuration.yaml is set up
- **YAML mode**: Follow manual setup in the Dashboard Setup section above
- Check the welcome notification for specific instructions for your setup

### Log File Auto-Detection Issues
- Integration will automatically try these paths in order:
  1. Your configured path
  2. `/config/home-assistant.log`
  3. `~/.homeassistant/home-assistant.log`
  4. `/usr/share/hassio/homeassistant/home-assistant.log`
- If none found, check Home Assistant logs for the full error message
- You can manually specify the correct path in integration configuration

## Getting Help

If you encounter issues:

1. Check the [README](README.md) for additional documentation
2. Search existing [GitHub Issues](https://github.com/cozbox/loggy/issues)
3. Create a new issue with:
   - Home Assistant version
   - Loggy AI version
   - Error messages from logs
   - Steps to reproduce

---

🎉 Congratulations! You've successfully installed Loggy AI!

For usage examples and advanced configuration, see the [README](README.md).