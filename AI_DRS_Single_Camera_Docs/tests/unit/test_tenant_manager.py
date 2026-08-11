"""
Unit tests for Multi-Tenant Organization & Stadium Venue Manager Module
"""

import pytest

from ai_drs.enterprise.tenant_manager import (
    OrganizationTenant,
    TenantManager,
    VenueInfo,
)


def test_tenant_manager_lifecycle():
    manager = TenantManager()

    # 1. Create Tenant
    tenant = manager.create_tenant("BCCI Cricket League", rate_limit_rpm=300)
    assert isinstance(tenant, OrganizationTenant)
    assert tenant.org_name == "BCCI Cricket League"
    assert tenant.api_key.startswith("sk_live_")

    # 2. Authenticate API Key
    auth_tenant = manager.authenticate_api_key(tenant.api_key)
    assert auth_tenant.tenant_id == tenant.tenant_id

    # 3. Register Venue
    venue = VenueInfo(
        venue_id="V_EDEN",
        venue_name="Eden Gardens",
        city="Kolkata",
        country="India"
    )
    manager.register_venue(tenant.tenant_id, venue)

    assert len(auth_tenant.venues) == 1
    assert auth_tenant.venues[0].venue_name == "Eden Gardens"


def test_tenant_auth_failures():
    manager = TenantManager()
    with pytest.raises(PermissionError):
        manager.authenticate_api_key("sk_invalid_999")
