# Loggy AI - Release Notes

## Version 1.1.0 - Home Assistant 2025+ Systemd Journal Support

### 🚀 Major New Feature

#### Systemd Journal Support (Critical for HA 2025+)
- **What Changed**: Home Assistant 2025+ writes logs ONLY to systemd journal (not to `/config/home-assistant.log`) to reduce disk writes on SBCs with SD cards
- **The Fix**: Loggy AI now supports **both** systemd journal AND file-based logging
- **100% Robust**: Automatically detects and uses the best available log source

**Smart Log Source Detection:**
1. **First**: Tries systemd journal (preferred for HA 2025+)
   - Reads directly from systemd journal
   - Filters by Home Assistant service identifiers
   - Supports configurable time ranges
2. **Fallback**: Tries log file at configured path
3. **Auto-detect**: Checks common log file locations

**Why This Matters:**
- ✅ **Future-proof**: Works with Home Assistant 2025+ journal-only logging
- ✅ **Backward compatible**: Still works with older file-based logging
- ✅ **Zero configuration**: Automatically detects the right source
- ✅ **SBC optimized**: No SD card wear from log files on newer HA versions
- ✅ **Dashboard compatible**: All features work with both log sources

### 🔧 Technical Changes

**New Dependencies:**
- Added `systemd-python>=235` for journal access
  - Gracefully handles systems without systemd
  - Automatically falls back to file-based logging

**Updated Files:**
- `coordinator.py`: Added `_read_from_systemd_journal()` method
- `utils.py`: Added `is_systemd_available()` helper function
- `const.py`: Added systemd journal identifier constants
- `manifest.json`: Updated version to 1.1.0, added systemd-python dependency

### 📚 Documentation Updates

**README.md:**
- Added Home Assistant 2025+ compatibility notice
- Explained smart log source detection
- Updated troubleshooting for both log sources

**INSTALLATION.md:**
- Added note about systemd journal support
- Clarified log file path is optional for HA 2025+
- Updated troubleshooting section with new detection logic

### 🔄 Migration Guide

**For All Users:**
- **No action required!** The integration automatically detects your log source
- Update via HACS or manually replace files
- Restart Home Assistant
- Integration will automatically use systemd journal if available

**For Home Assistant 2025+ Users:**
- Your logs will now be read from systemd journal
- No more log file needed
- Reduced SD card writes (better for SBC longevity)
- All dashboard features work exactly the same

**For Older Home Assistant Versions:**
- Continues to work exactly as before
- Reads from log file at configured path
- Automatically falls back if systemd unavailable

### 🔒 Security

- ✅ No vulnerabilities in systemd-python dependency
- ✅ All existing security features maintained
- ✅ Graceful error handling for missing permissions
- ✅ CodeQL security scan clean

### 🧪 Testing

- ✅ JSON syntax validation passed
- ✅ YAML syntax validation passed
- ✅ Python syntax validation passed
- ✅ Systemd journal reading tested and verified
- ✅ Fallback to file-based logging verified
- ✅ Dashboard compatibility verified

### 📦 Dependencies

**Added:**
- `systemd-python>=235` - For systemd journal access

**Unchanged:**
- `google-genai>=1.51.0`
- `openai==1.54.0`
- `anthropic==0.39.0`

### 🎯 Compatibility

**Tested With:**
- ✅ Home Assistant 2025+ (systemd journal)
- ✅ Home Assistant 2024.x (file-based logging)
- ✅ Home Assistant OS
- ✅ Home Assistant Supervised
- ✅ Home Assistant Core
- ✅ Docker installations
- ✅ Raspberry Pi and other SBCs

### 🙏 Acknowledgments

Thanks to the Home Assistant community for raising awareness about the 2025+ logging changes and ensuring Loggy AI remains 100% compatible!

---

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
