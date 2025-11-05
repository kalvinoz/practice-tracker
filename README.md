# Practice Tracker - Home Assistant Custom Integration

**Status:** Early Development (v0.1.0)

A flexible Home Assistant custom integration for tracking practice/usage time on instruments, exercise equipment, or any activity with detectable usage.

## Features (v0.1.0 - MVP)

- ✅ UI-based configuration (no YAML editing required)
- ✅ Support for 1-8 players/users
- ✅ Player selection entity
- ⏳ History tracking sensors (coming in v0.2.0)
- ⏳ ESP32 touchscreen display support (coming in v0.3.0)

## Installation

### Development Installation

1. Copy the `custom_components/practice_tracker` directory to your Home Assistant `custom_components` folder:
   ```
   /config/custom_components/practice_tracker/
   ```

2. Restart Home Assistant

3. Go to **Settings → Devices & Services → Add Integration**

4. Search for "Practice Tracker"

5. Follow the configuration wizard:
   - Enter tracker name (e.g., "Piano Practice")
   - Choose number of players (1-8)
   - Enter player names
   - Select trigger binary sensor

### Configuration

The integration creates a `select` entity for player selection:
- `select.{tracker_name}_current_player`

Options: None, {player1}, {player2}, ..., Other

## Use Cases

- **Music Practice**: Piano, guitar, drums, violin
- **Exercise Equipment**: Treadmill, rowing machine, stationary bike
- **Study Time**: Desk usage tracking
- **Shared Resources**: Workshop tools, game consoles

## Development

Based on the working piano practice tracker implementation.

### Roadmap

- **v0.1.0** (Current): Basic config flow + player selection
- **v0.2.0**: History stats sensors
- **v0.3.0**: ESP32 display component
- **v1.0.0**: Public release via HACS

## License

MIT

## Author

Pedro Queiroz
