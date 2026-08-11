"""
Broadcaster DRS Decision Card & Split-Screen Overlay Renderer for TV Production
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field

from ai_drs.api.review_service import ReviewResultResponse
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.graphics.overlay")


class BroadcastDRSOverlayCard(BaseModel):
    """Schema representing TV broadcast-ready DRS decision overlay card."""
    review_id: str
    pitching_badge: str = Field(description="'PITCHING: IN LINE', 'PITCHING: OUTSIDE OFF', 'PITCHING: OUTSIDE LEG'")
    impact_badge: str = Field(description="'IMPACT: IN LINE', 'IMPACT: OUTSIDE OFF', 'IMPACT: OUTSIDE LEG'")
    wickets_badge: str = Field(description="'WICKETS: HITTING', 'WICKETS: MISSING', 'WICKETS: CLIPPING'")
    final_decision_badge: str = Field(description="'OUT', 'NOT OUT', 'INCONCLUSIVE'")
    confidence_pct: float
    svg_overlay_xml: str


class BroadcastOverlayEngine:
    """Renders TV production broadcast DRS decision cards and SVG graphic overlays."""

    @staticmethod
    def render_drs_decision_card(review: ReviewResultResponse) -> BroadcastDRSOverlayCard:
        """Renders TV decision card badges and SVG graphic overlay XML."""
        p_badge = f"PITCHING: {review.evidence.pitching_zone.value.upper()}"
        i_badge = f"IMPACT: {review.evidence.impact_zone.value.upper()}"
        w_badge = f"WICKETS: {review.evidence.hit_stumps_status.value.upper()}"
        final_badge = review.decision.value.upper()

        status_color = "#00E676" if final_badge == "OUT" else ("#FF1744" if final_badge == "NOT OUT" else "#FFEA00")

        svg_xml = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="350" viewBox="0 0 600 350">
  <rect width="600" height="350" rx="12" fill="#0A0A0C" stroke="#2A2A32" stroke-width="2"/>
  <text x="30" y="45" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#00E676">🏏 AI DRS DECISION REVIEW</text>
  <text x="570" y="45" font-family="Arial, sans-serif" font-size="14" fill="#A0A0B0" text-anchor="end">ID: {review.review_id[:8]}</text>
  <line x1="30" y1="65" x2="570" y2="65" stroke="#2A2A32" stroke-width="2"/>
  
  <rect x="30" y="90" width="540" height="45" rx="6" fill="#16161E"/>
  <text x="50" y="118" font-family="Arial, sans-serif" font-size="16" fill="#FFFFFF">{p_badge}</text>
  
  <rect x="30" y="145" width="540" height="45" rx="6" fill="#16161E"/>
  <text x="50" y="173" font-family="Arial, sans-serif" font-size="16" fill="#FFFFFF">{i_badge}</text>
  
  <rect x="30" y="200" width="540" height="45" rx="6" fill="#16161E"/>
  <text x="50" y="228" font-family="Arial, sans-serif" font-size="16" fill="#FFFFFF">{w_badge}</text>
  
  <rect x="30" y="260" width="540" height="60" rx="8" fill="{status_color}"/>
  <text x="300" y="300" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">{final_badge}</text>
</svg>"""

        logger.info(f"Rendered TV Broadcast DRS Decision Card [{review.review_id}]: {final_badge}")

        return BroadcastDRSOverlayCard(
            review_id=review.review_id,
            pitching_badge=p_badge,
            impact_badge=i_badge,
            wickets_badge=w_badge,
            final_decision_badge=final_badge,
            confidence_pct=round(review.confidence_score * 100.0, 1),
            svg_overlay_xml=svg_xml
        )
