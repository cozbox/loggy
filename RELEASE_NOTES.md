# Loggy AI - Release Notes

## Version 1.0.1 - Dependency Fix & Dashboard Enhancement

### 🐛 Bug Fixes

#### Fixed Dependency Conflict
- **Issue**: Installation failed with protobuf version conflict
- **Error**: `google-generativeai==0.8.3` had incompatible protobuf requirements causing:
  ```
  google-ai-generativelanguage==0.6.10 depends on protobuf<6.0.0.dev0
  google-generativeai==0.8.3 depends on protobuf==6.32.0
  → Requirements are unsatisfiable
  ```
- **Solution**: Updated to `google-generativeai==0.8.5`
  - Uses `google-ai-generativelanguage==0.6.15` with flexible protobuf support
  - Fully compatible with Home Assistant's dependency resolver
  - Maintains all existing functionality

### ✨ New Features

#### Pre-configured Dashboard
Added `loggy_ai_dashboard.yaml` - a complete, ready-to-use dashboard that includes:

**Dashboard Components:**
- 📊 **Main Loggy AI Card**: Custom card displaying all analysis data
- 🎯 **Quick Actions**: One-click button to trigger analysis
- 📈 **Statistics Grid**: Real-time counts for:
  - Errors (red)
  - Warnings (yellow)
  - New Issues (blue)
- 📉 **Historical Trends**: 7-day graph of error/warning patterns
- 📝 **Full Analysis**: Complete AI analysis with markdown formatting

**Easy Setup:**
1. Download `loggy_ai_dashboard.yaml`
2. Go to Settings → Dashboards → Add Dashboard
3. Name it "Loggy AI" with robot icon
4. Edit dashboard → Raw YAML editor
5. Paste and save!

### 📚 Documentation Updates

Enhanced README.md with:
- Step-by-step dashboard setup instructions
- Two setup options (new dashboard or add to existing)
- Quick start guide in initial configuration section
- Clear visual indicators for what's included

### 🔄 Migration Guide

**Existing Users:**
1. Update the integration via HACS or manually
2. Restart Home Assistant
3. Dependencies will automatically update to v0.8.5
4. (Optional) Import the new dashboard for enhanced experience

**New Users:**
- Follow standard installation process
- No special steps required
- Dashboard setup is optional but recommended

### 🔒 Security

- No security vulnerabilities in updated dependencies
- All existing security features maintained
- API keys remain securely stored

### 🧪 Testing

- ✅ JSON syntax validation passed
- ✅ YAML syntax validation passed
- ✅ Python syntax validation passed
- ✅ Security advisory check passed
- ✅ Template syntax updated to current standards

### 📦 Dependencies

**Updated:**
- `google-generativeai`: 0.8.3 → 0.8.5

**Unchanged:**
- `openai==1.54.0`
- `anthropic==0.39.0`

### 🙏 Acknowledgments

Thanks to the Home Assistant community for reporting the dependency issue and requesting dashboard improvements!
