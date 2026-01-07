from contextvars import ContextVar


class ContextVarsContainer:
    def __init__(self):
        self.trace_id = ContextVar("trace_id", default="local")

    @property
    def context_vars(self) -> dict:
        return {"trace_id": self.trace_id.get()}

    def set_trace_id(self, trace_id: str):
        self.trace_id.set(trace_id)


__all__ = ["ContextVarsContainer"]