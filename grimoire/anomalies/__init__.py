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
Anomaly Detection System

This package provides a comprehensive anomaly detection framework for the
Grimoire programming language, including base classes, registry management,
and integration mixins.
"""

from .base import BaseAnomaly, CompositeAnomaly, AdaptiveAnomaly, AnomalyReport
from .registry import AnomalyRegistry, anomaly_registry, get_anomaly, get_anomaly_set, register_anomaly
from .mixins import (
    AnomalyDetectorMixin, 
    ContextAwareAnomalyMixin,
    game_mode_context_rule,
    time_based_context_rule,
    load_based_context_rule,
    business_period_context_rule
)

__all__ = [
    # Base classes
    "BaseAnomaly",
    "CompositeAnomaly", 
    "AdaptiveAnomaly",
    "AnomalyReport",
    
    # Registry
    "AnomalyRegistry",
    "anomaly_registry",
    "get_anomaly",
    "get_anomaly_set", 
    "register_anomaly",
    
    # Mixins
    "AnomalyDetectorMixin",
    "ContextAwareAnomalyMixin",
    
    # Context rules
    "game_mode_context_rule",
    "time_based_context_rule", 
    "load_based_context_rule",
    "business_period_context_rule"
]