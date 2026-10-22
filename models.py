"""Object-oriented packet models and an explainable AI-inspired routing policy."""
from abc import ABC, abstractmethod


class PacketError(ValueError):
    """Raised when a packet has invalid input."""


class Packet(ABC):
    """Abstract parent class for all data waiting to be transmitted."""

    mode = "Unknown"
    base_priority = 0
    minimum_signal = 0

    def __init__(self, size_bytes: int, urgency: int, note: str = ""):
        if size_bytes <= 0:
            raise PacketError("Packet size must be greater than zero.")
        if not 1 <= urgency <= 5:
            raise PacketError("Urgency must be from 1 to 5.")
        self.size_bytes = int(size_bytes)
        self.urgency = int(urgency)
        self.note = note.strip()

    @abstractmethod
    def priority(self) -> int:
        """Return a base priority; higher values are considered first."""

    @abstractmethod
    def minimum_link(self) -> int:
        """Return the minimum signal percentage for this mode."""

    def transmission_seconds(self, signal: int) -> float:
        """Estimate transfer time using a simple simulated throughput model."""
        effective_rate = max(1, 900 * (signal / 100))
        return round((self.size_bytes * 8) / effective_rate, 1)


class Telemetry(Packet):
    mode = "TT&C / Health"
    base_priority = 100
    minimum_signal = 10

    def priority(self):
        return self.base_priority + self.urgency * 2

    def minimum_link(self):
        return self.minimum_signal


class ImagePacket(Packet):
    mode = "SSTV Image"
    base_priority = 50
    minimum_signal = 50

    def priority(self):
        return self.base_priority + self.urgency * 2

    def minimum_link(self):
        return self.minimum_signal


class DigitalVoice(Packet):
    mode = "M17 / Codec2 Voice"
    base_priority = 30
    minimum_signal = 40

    def priority(self):
        return self.base_priority + self.urgency * 2

    def minimum_link(self):
        return self.minimum_signal


PACKET_TYPES = {
    "TT&C / Health": Telemetry,
    "SSTV Image": ImagePacket,
    "M17 / Codec2 Voice": DigitalVoice,
}


def routing_score(packet: Packet, signal: int, battery: int) -> float:
    """A small, explainable heuristic score for simulation, not a trained ML model.

    Critical telemetry receives a strong priority boost. Low battery reduces the
    score of non-critical traffic so the simulation can conserve resources.
    """
    score = float(packet.priority())
    if packet.mode != "TT&C / Health" and battery < 25:
        score -= 18
    if signal < packet.minimum_link():
        score -= 1000
    if battery < 8:
        score -= 1000
    return score
