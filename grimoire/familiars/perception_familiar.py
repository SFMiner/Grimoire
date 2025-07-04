from __future__ import annotations

from typing import Optional

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType

import importlib

def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("Perception")
class PerceptionFamiliar(_base_cls()):
    """Familiar that provides environmental perception capabilities."""

    def __init__(self, name: str, *, vision_range: int = 5, true_name: Optional[str] = None):
        super().__init__(name, "Perception", capabilities={}, true_name=true_name)
        self.category = FamiliarType.PERCEPTION
        self.vision_range = vision_range

        self.add_socket("perception_output", direction="output")

    def scan_environment(self):
        # Placeholder – would hook into world model
        perceived = {"entities": [], "resources": []}
        self.send_to_socket("perception_output", perceived)

    def autonomous_update(self):
        super().autonomous_update()
        self.scan_environment()