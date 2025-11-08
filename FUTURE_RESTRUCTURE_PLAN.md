# Future Restructure Plan: Complete Installation Package

**Version:** 1.0.0 (Public Release)
**Roadmap Alignment:** This plan executes as part of v1.0.0 milestone

## Goal

Transform the practice-tracker repository from a Home Assistant custom component only into a **complete, ready-to-install package** that anyone with an ESP32-S3-Box-3 can download and use immediately.

This aligns with the roadmap goal of v1.0.0: Public release via HACS with complete documentation and example configurations.

## Current State

**practice-tracker repo** (standalone)
```
practice-tracker/
├── custom_components/
│   └── practice_tracker/          # HA integration only
├── .gitignore
└── README.md
```

**homeassistant repo** (separate, contains related files)
- `esphome/esp32-s3-box-3-640618.yaml` - ESP32 display configuration
- `packages/piano/` - HA automations and sensors
- `www/audio/` - Sound files (boot.flac, start.flac, end.flac)
- `www/images/piano.jpg` - Background image

## Target State

**practice-tracker repo** (all-in-one package)
```
practice-tracker/
├── custom_components/
│   └── practice_tracker/          # Home Assistant integration
│       ├── __init__.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── select.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── esphome/
│   ├── piano-display.yaml         # ESP32 configuration (template)
│   └── secrets_template.yaml      # Template for user secrets
├── packages/
│   └── piano_practice/
│       ├── package.yaml            # HA package configuration
│       ├── automations.yaml        # Piano automations
│       ├── sensors.yaml            # Piano sensors
│       └── templates.yaml          # Piano templates
├── www/
│   ├── audio/
│   │   ├── boot.flac
│   │   ├── start.flac
│   │   └── end.flac
│   └── images/
│       └── piano.jpg
├── docs/
│   ├── INSTALLATION.md             # Complete installation guide
│   ├── HARDWARE.md                 # Hardware requirements and setup
│   ├── TROUBLESHOOTING.md          # Common issues and solutions
│   └── CUSTOMIZATION.md            # How to customize player names, sounds, etc.
├── scripts/
│   └── install.sh                  # Optional: installation helper script
├── .gitignore
├── README.md                       # Overview and quick start
├── hacs.json                       # HACS integration metadata
└── LICENSE
```

## Migration Steps

### 1. Prepare the Repository Structure

```bash
cd /Users/pqz/Code/practice-tracker

# Create new directories
mkdir -p esphome
mkdir -p packages/piano_practice
mkdir -p www/audio
mkdir -p www/images
mkdir -p docs
mkdir -p scripts
```

### 2. Copy Files from homeassistant Repo

**ESP32 Configuration**
```bash
# Copy and templatize ESP32 config
cp /Users/pqz/Code/homeassistant/esphome/esp32-s3-box-3-640618.yaml \
   esphome/piano-display.yaml

# Edit to:
# - Replace hardcoded ha_url with substitution variable
# - Add secrets_template.yaml with example values
# - Add comments explaining customization points
```

**HA Package Configuration**
```bash
# Copy piano package files
cp -r /Users/pqz/Code/homeassistant/packages/piano/* \
      packages/piano_practice/

# Edit to ensure it's self-contained
```

**Media Files**
```bash
# Copy audio files
cp /Users/pqz/Code/homeassistant/www/audio/*.flac www/audio/

# Copy image
cp /Users/pqz/Code/homeassistant/www/images/piano.jpg www/images/
```

### 3. Create Documentation

**README.md** - Quick overview
- What it does
- Hardware requirements (ESP32-S3-Box-3)
- Quick installation steps
- Screenshots/demo video
- Link to detailed docs

**docs/INSTALLATION.md** - Step-by-step guide
1. Prerequisites check
2. Install HA custom component
3. Copy package to HA config
4. Copy media files to www/
5. Flash ESP32 with ESPHome config
6. Configure integration in HA UI
7. Verification steps

**docs/HARDWARE.md** - Hardware details
- ESP32-S3-Box-3 specifications
- Where to buy
- Assembly instructions (if any)
- Power supply recommendations
- Mounting suggestions

**docs/TROUBLESHOOTING.md** - Common issues
- ESP32 won't flash
- Display not showing
- HA integration not working
- Audio not playing
- Connectivity issues

**docs/CUSTOMIZATION.md** - How to customize
- Changing player names
- Replacing audio files
- Customizing colors/layout
- Adding more players
- Adjusting time tracking periods

### 4. Templatize ESP32 Configuration

Make the ESP32 config user-friendly:

```yaml
# esphome/piano-display.yaml
substitutions:
  name: piano-display
  friendly_name: Piano Display
  # USER: Change this to your Home Assistant URL
  ha_url: "http://homeassistant.local:8123"

  # USER: Customize player names (4 max)
  player_1: "Claire"
  player_2: "Pedro"
  player_3: "Sofia"
  player_4: "Charlie"

# ... rest of config uses ${player_1}, ${player_2}, etc.
```

Create `esphome/secrets_template.yaml`:
```yaml
# Copy this to secrets.yaml in your ESPHome directory
# and fill in your actual values

wifi_ssid: "YourWiFiSSID"
wifi_password: "YourWiFiPassword"
api_encryption_key: "your-32-character-encryption-key-here"
```

### 5. Make Package Configuration Portable

Ensure the HA package works standalone:

```yaml
# packages/piano_practice/package.yaml

# Piano Practice Tracker Package
# Auto-creates all necessary entities

input_select:
  piano_current_player:
    name: "Current Piano Player"
    options:
      - "None"
      - "Claire"
      - "Pedro"
      - "Sofia"
      - "Charlie"
    initial: "None"
    icon: mdi:piano

input_number:
  piano_daily_seconds_claire:
    name: "Claire Daily Practice Time"
    min: 0
    max: 86400
    step: 1
    unit_of_measurement: "s"
    mode: box
    icon: mdi:timer
  # ... etc for other players

# Include automations, sensors, templates
automation: !include automations.yaml
sensor: !include sensors.yaml
template: !include templates.yaml
```

### 6. Add HACS Integration Support

Create `hacs.json`:
```json
{
  "name": "Piano Practice Tracker",
  "render_readme": true,
  "domains": ["select", "sensor"],
  "homeassistant": "2024.1.0",
  "iot_class": "Local Polling"
}
```

### 7. Create Installation Script (Optional)

```bash
#!/bin/bash
# scripts/install.sh
# Interactive installation helper for Piano Practice Tracker

echo "Piano Practice Tracker - Installation Helper"
echo "============================================="
echo ""

# Check if running in HA config directory
if [ ! -d "custom_components" ]; then
    echo "Error: Please run this from your Home Assistant config directory"
    exit 1
fi

# ... interactive prompts for installation
```

### 8. Update README.md

Make it compelling and clear:

```markdown
# 🎹 Piano Practice Tracker

A complete Home Assistant integration with ESP32-S3-Box-3 display for tracking piano practice time across multiple players.

## ✨ Features

- 📊 Track daily practice time for up to 4 players
- 🖥️ Beautiful touchscreen display with player selection
- 🎵 Audio feedback for practice sessions
- 📈 Historical statistics and analytics
- 🔄 Automatic midnight reset
- 🎨 Customizable player names and sounds

## 🛠️ Hardware Requirements

- ESP32-S3-Box-3 ($50)
- Home Assistant instance
- Smart plug to monitor piano power (optional but recommended)

## 🚀 Quick Start

1. **Install the Integration**
   - Copy `custom_components/practice_tracker` to your HA config
   - Restart Home Assistant
   - Add integration via Settings → Devices & Services

2. **Flash the Display**
   - Copy `esphome/piano-display.yaml` to ESPHome
   - Customize player names in substitutions
   - Flash to your ESP32-S3-Box-3

3. **Add Package Configuration**
   - Copy `packages/piano_practice` to your HA config packages/
   - Copy `www/` contents to your HA www/ directory
   - Restart Home Assistant

[Full Installation Guide](docs/INSTALLATION.md)

## 📸 Screenshots

[Add screenshots of display and HA dashboard]

## 🎯 How It Works

[Explain the system briefly]

## 🤝 Contributing

[Contribution guidelines]

## 📄 License

MIT License
```

## Installation Experience for End Users

After restructure, a user would:

1. **Clone or download the repo**
   ```bash
   git clone https://github.com/kalvinoz/practice-tracker
   ```

2. **Install HA integration**
   - Copy `custom_components/practice_tracker` to HA config
   - OR: Install via HACS (future)

3. **Copy package**
   ```bash
   cp -r practice-tracker/packages/piano_practice /config/packages/
   ```

4. **Copy media files**
   ```bash
   cp -r practice-tracker/www/* /config/www/
   ```

5. **Flash ESP32**
   - Open `esphome/piano-display.yaml` in ESPHome
   - Customize substitutions (player names, HA URL)
   - Create secrets.yaml from template
   - Flash to device

6. **Configure in HA**
   - Add integration via UI
   - Configure players
   - Done!

## Benefits of This Approach

1. **One-Stop Shop**: Everything needed in one repository
2. **Version Compatibility**: ESP32 config and integration stay in sync
3. **Easy Distribution**: Can share one link, users get everything
4. **HACS Ready**: Can eventually submit to HACS for easy installation
5. **Complete Documentation**: All docs in one place
6. **Example Configs**: Users see working examples immediately

## Current Submodule Setup

The homeassistant repo currently uses practice-tracker as a submodule:
```
homeassistant/
├── submodules/
│   └── practice-tracker/          # Git submodule
└── custom_components/
    └── practice_tracker -> ../submodules/practice-tracker/custom_components/practice_tracker
```

After restructure, this would remain the same - the symlink would just point to a more comprehensive submodule.

## Roadmap Context

**Current Roadmap** (from README.md):
- ✅ **v0.1.0** (Current): Basic config flow + player selection
- ⏳ **v0.2.0**: History stats sensors
- ⏳ **v0.3.0**: ESP32 display component
- ⏳ **v1.0.0**: Public release via HACS + **THIS RESTRUCTURE**

**Prerequisites Before Restructure:**
1. v0.2.0 must be complete (history tracking sensors implemented)
2. v0.3.0 must be complete (ESP32 display integration tested)
3. Core functionality tested with multiple users
4. All known bugs fixed
5. Ready for public distribution

## When to Execute This Plan

Execute this restructure when:
- [ ] v0.2.0 complete (history stats sensors working)
- [ ] v0.3.0 complete (ESP32 display integration stable)
- [ ] Core integration is stable and tested
- [ ] Ready to share with community
- [ ] Documentation is ready to be written
- [ ] Have time for proper testing of the new structure
- [ ] Ready to submit to HACS

## Execution Command

When ready, tell Claude Code:

> "Execute the restructure plan in FUTURE_RESTRUCTURE_PLAN.md for the practice-tracker repository"

Claude Code will then:
1. Read this plan
2. Execute the migration steps
3. Create all documentation
4. Set up the new structure
5. Test that everything works
6. Update the README with the new installation instructions

---

**Status**: 📋 PLANNED - Not yet executed
**Last Updated**: November 8, 2025
**Version**: 1.0
