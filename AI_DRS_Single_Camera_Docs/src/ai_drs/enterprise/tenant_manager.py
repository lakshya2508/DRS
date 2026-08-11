"""
Multi-Tenant Organization & Stadium Venue Manager for Enterprise Cloud AI DRS
"""

import secrets
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.tenant")


class VenueInfo(BaseModel):
    """Schema representing a cricket stadium/ground venue."""
    venue_id: str
    venue_name: str
    city: str
    country: str
    pitch_length_m: float = 20.12


class OrganizationTenant(BaseModel):
    """Schema representing a tenant organization (League, Board, Broadcaster)."""
    tenant_id: str
    org_name: str
    api_key: str
    rate_limit_rpm: int = 120
    venues: List[VenueInfo] = Field(default_factory=list)
    is_active: bool = True


class TenantManager:
    """Manages enterprise tenant organizations, API key authentication, and venue registries."""

    def __init__(self):
        # Tenant ID -> OrganizationTenant
        self.tenants_by_id: Dict[str, OrganizationTenant] = {}
        # API Key -> Tenant ID
        self.api_key_map: Dict[str, str] = {}

    def create_tenant(self, org_name: str, rate_limit_rpm: int = 120) -> OrganizationTenant:
        """Registers a new tenant organization and generates secure API key."""
        tenant_id = f"org_{secrets.token_hex(4)}"
        api_key = f"sk_live_{secrets.token_hex(16)}"

        tenant = OrganizationTenant(
            tenant_id=tenant_id,
            org_name=org_name,
            api_key=api_key,
            rate_limit_rpm=rate_limit_rpm
        )

        self.tenants_by_id[tenant_id] = tenant
        self.api_key_map[api_key] = tenant_id

        logger.info(f"Registered Tenant Organization [{org_name}] with Tenant ID [{tenant_id}]")
        return tenant

    def authenticate_api_key(self, api_key: str) -> OrganizationTenant:
        """Validates API key and returns authenticated tenant organization."""
        if api_key not in self.api_key_map:
            raise PermissionError("Invalid or missing API key.")

        tenant_id = self.api_key_map[api_key]
        tenant = self.tenants_by_id[tenant_id]

        if not tenant.is_active:
            raise PermissionError("Tenant organization account is suspended.")

        return tenant

    def register_venue(self, tenant_id: str, venue: VenueInfo):
        """Registers a stadium venue under a tenant organization."""
        if tenant_id not in self.tenants_by_id:
            raise KeyError(f"Tenant ID '{tenant_id}' not found.")

        self.tenants_by_id[tenant_id].venues.append(venue)
        logger.info(f"Registered Venue [{venue.venue_name}] under Tenant [{tenant_id}]")


# Global tenant manager instance
tenant_manager = TenantManager()
