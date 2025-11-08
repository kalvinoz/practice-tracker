# Blocking Database Call Fix

**Date:** November 8, 2025
**Version:** Commit df93ec6
**Issue:** RuntimeError in Python 3.13 asyncio strict mode

## Problem

The practice tracker sensors were making blocking database calls from the `native_value` property:

```python
@property
def native_value(self) -> float | None:
    # This blocking call caused RuntimeError
    history_list = history.state_changes_during_period(
        self.hass,
        start,
        end,
        self._select_entity_id,
    )
```

### Error Message

```
RuntimeError: Caught blocking call to _do_get_db_connection_protected
with args None inside the event loop by integration 'recorder' at
homeassistant/components/recorder/pool.py, line 104
```

This error occurred because:
1. `history.state_changes_during_period()` makes a SQLAlchemy database connection
2. Database connections are blocking I/O operations
3. Python 3.13's asyncio strict mode detects blocking calls in the event loop
4. Home Assistant's recorder enforces this restriction

## Solution

### Changes Made

1. **Added state cache**
   - Added `self._state: float | None = None` in `__init__()`
   - Stores the calculated practice time

2. **Extracted history calculation**
   - Created `_calculate_history()` method that runs the blocking database query
   - This method runs in the executor, not the event loop

3. **Moved logic to async_update()**
   - The `async_update()` method now calls the history calculation
   - Uses `await self.hass.async_add_executor_job()` to run blocking code safely

4. **Simplified native_value property**
   - Now simply returns the cached `self._state` value
   - No blocking operations in property getter

### Code Structure

```python
class PracticeHistorySensor(SensorEntity):
    def __init__(self, ...):
        self._state: float | None = None  # Cache for calculated value

    def _calculate_history(self, start: datetime, end: datetime) -> float:
        """Calculate practice time from history (runs in executor)."""
        # Blocking database call happens here, but it's OK because
        # this runs in the executor, not the event loop
        history_list = history.state_changes_during_period(...)
        # ... calculate total time ...
        return hours

    @property
    def native_value(self) -> float | None:
        """Return the cached state."""
        return self._state  # Simple, non-blocking

    async def async_update(self) -> None:
        """Update the sensor by running blocking code in executor."""
        start, end = self._get_period_start_end()

        # Run blocking history query safely in executor
        self._state = await self.hass.async_add_executor_job(
            self._calculate_history, start, end
        )
```

## Why This Works

**Executor Jobs:**
- `async_add_executor_job()` runs the function in a thread pool
- Thread pool operations don't block the event loop
- Database calls are safe in thread pool
- The `await` properly yields control back to event loop while waiting

**Property vs Method:**
- Properties (`@property`) are expected to be fast, non-blocking
- They can be called at any time during rendering or state access
- Async methods (`async def`) can perform slow operations safely
- Home Assistant calls `async_update()` periodically with proper scheduling

## Testing

After this fix:
- ✅ No more RuntimeError in logs
- ✅ Sensors update correctly every scan_interval
- ✅ History calculations work as expected
- ✅ Compatible with Python 3.13 strict asyncio mode

## Related Issues

This same pattern should be applied to any custom component that:
- Queries the recorder/history database
- Uses SQLAlchemy directly
- Makes file I/O operations
- Calls external APIs without using async libraries

All such operations should be wrapped in `async_add_executor_job()`.

## References

- [Home Assistant Async Documentation](https://developers.home-assistant.io/docs/asyncio_blocking_operations/)
- [Python asyncio Best Practices](https://docs.python.org/3/library/asyncio-dev.html)
- [SQLAlchemy in Async Context](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
