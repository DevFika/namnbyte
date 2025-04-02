class Signal:
    """Custom Signal class that allows connecting functions (observers) and emitting events."""
    
    def __init__(self):
        self._slots = []
        self._suppress = False
    
    def connect(self, slot):
        """Connect an observer (function) to this signal."""
        if slot not in self._slots:
            self._slots.append(slot)

    def disconnect(self, slot):
        """Disconnect an observer (function) from this signal."""
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, data=None, *args, **kwargs):
        """
        Emit the signal with the provided data to all connected observers.
        
        Additional args and kwargs will be passed to each connected slot.
        """
        if not self._suppress:
            for slot in self._slots:
                slot(data, *args, **kwargs)


    def suppress(self):
        """Turn off all signals temporarily."""
        self._suppress = True

    def resume(self, final_data=None, *args, **kwargs):
        """Turn signals back on, and optionally emit a final update."""
        self._suppress = False
        if final_data is not None:
            self.emit(final_data, *args, **kwargs)


class InformationSignal(Signal):
    def emit_info(self, message, context="info", *args, **kwargs):
        """Emit an informational message."""
        self.emit({
            "message": message,
            "type": "info",
            "context": context
        }, *args, **kwargs)

    def emit_warning(self, message, context="warning", *args, **kwargs):
        """Emit a warning message."""
        self.emit({
            "message": message,
            "type": "warning",
            "context": context
        }, *args, **kwargs)

    def emit_error(self, message, context="error", *args, **kwargs):
        """Emit an error message."""
        self.emit({
            "message": message,
            "type": "error",
            "context": context
        }, *args, **kwargs)

    def emit_success(self, message, context="success", *args, **kwargs):
        """Emit an error message."""
        self.emit({
            "message": message,
            "type": "success",
            "context": context
        }, *args, **kwargs)
