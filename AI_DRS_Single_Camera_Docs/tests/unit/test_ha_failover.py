"""
Unit tests for High-Availability Failover & Load Balancer Health Probe Module
"""

import pytest

from ai_drs.enterprise.ha_failover import ClusterNodeHealth, HAFailoverManager


def test_ha_failover_normal():
    ha = HAFailoverManager("primary_01", "standby_02")
    status = ha.check_node_health("primary_01", is_healthy=True)

    assert isinstance(status, ClusterNodeHealth)
    assert status.is_healthy is True
    assert ha.active_routing_node_id == "primary_01"


def test_ha_failover_trigger():
    ha = HAFailoverManager("primary_01", "standby_02")
    # Simulate primary crash
    status = ha.check_node_health("primary_01", is_healthy=False)

    assert status.is_healthy is False
    assert ha.active_routing_node_id == "standby_02"  # Automatic Failover
