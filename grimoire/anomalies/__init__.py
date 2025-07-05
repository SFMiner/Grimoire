# Grimoire Programming Language
# Copyright (C) 2025 Sean Miner
#
# This file is part of Grimoire.
#
# Grimoire is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Grimoire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Grimoire Anomaly Detection System

A comprehensive anomaly detection framework integrated with Grimoire's
agent hierarchy for proactive problem detection and automated escalation.

This system transforms expensive periodic searches into efficient, agent-driven
detection through programmable Anomaly artifacts.
"""

from .base import BaseAnomaly, CompositeAnomaly, AdaptiveAnomaly
from .registry import (
    AnomalyRegistry, anomaly_registry,
    register_anomaly, get_anomaly, create_anomaly_set, get_anomaly_set, add_context_rule
)

__version__ = "1.0.0"
__all__ = [
    "BaseAnomaly", 
    "CompositeAnomaly", 
    "AdaptiveAnomaly",
    "AnomalyRegistry", 
    "anomaly_registry",
    "register_anomaly",
    "get_anomaly", 
    "create_anomaly_set",
    "get_anomaly_set",
    "add_context_rule"
]