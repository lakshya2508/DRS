"""
High-Availability Failover & Load Balancer Health Probe Module
"""

from typing import Dict, List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.ha_failover")


class ClusterNodeHealth(BaseModel):
    """Schema representing cluster node health status for load balancers."""
    node_id: str
    is_primary: bool
    is_healthy: bool
    load_score: float = Field(ge=0.0, le=1.0)
    failover_ready: bool


class HAFailoverManager:
    """Manages active-standby cluster node failover routing for 99.999% uptime live broadcasts."""

    def __init__(self, primary_node_id: str = "node_primary_01", standby_node_id: str = "node_standby_02"):
        self.primary_node_id = primary_node_id
        self.standby_node_id = standby_node_id
        self.active_routing_node_id = primary_node_id
        self.primary_healthy = True

    def check_node_health(self, node_id: str, is_healthy: bool) -> ClusterNodeHealth:
        """Checks and updates health status for cluster node."""
        if node_id == self.primary_node_id:
            self.primary_healthy = is_healthy
            if not is_healthy and self.active_routing_node_id == self.primary_node_id:
                # Trigger Failover to Standby
                self.active_routing_node_id = self.standby_node_id
                logger.warning(f"CRITICAL FAILOVER TRIGGERED: Rerouted traffic from [{self.primary_node_id}] to [{self.standby_node_id}]")

        is_primary = (node_id == self.primary_node_id)
        logger.debug(f"HA Health Check [{node_id}]: healthy={is_healthy}, active_node={self.active_routing_node_id}")

        return ClusterNodeHealth(
            node_id=node_id,
            is_primary=is_primary,
            is_healthy=is_healthy,
            load_score=0.25 if is_healthy else 1.0,
            failover_ready=True
        )
