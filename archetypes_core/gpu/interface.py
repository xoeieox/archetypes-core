"""Abstract GPU coordination interface.

Products subclass this with their own implementation.
Default is a no-op (always available) for environments without GPU contention.
"""


class GPUCoordinator:
    """GPU resource coordinator. Override for shared-GPU environments."""

    def acquire(self, caller: str) -> None:
        """Signal that caller needs the GPU."""

    def release(self, caller: str) -> None:
        """Signal that caller is done with the GPU."""

    def is_available(self) -> bool:
        """Check if the GPU is available."""
        return True

    def wait(self, timeout: float = 30.0) -> bool:
        """Wait for GPU availability. Returns True if acquired."""
        return True
