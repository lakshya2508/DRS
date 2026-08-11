"""
Unit tests for WebRTC Smartphone Live Camera Ingestion Gateway Module
"""

import cv2
import numpy as np
import pytest

from ai_drs.ingestion.webrtc_ingester import SDPOfferSession, WebRTCLiveStreamGateway


def test_webrtc_sdp_handshake_and_frame_decoding():
    gateway = WebRTCLiveStreamGateway()

    # 1. Test SDP Handshake
    offer_sdp = "v=0\r\no=- 123 2 IN IP4 127.0.0.1\r\ns=OFFER"
    session = gateway.create_peer_connection("CAM_MOBILE_01", offer_sdp)

    assert isinstance(session, SDPOfferSession)
    assert session.camera_id == "CAM_MOBILE_01"
    assert session.is_connected is True
    assert "AI_DRS_LIVE" in session.sdp_answer

    # 2. Test Live Frame Decoding
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, encoded_jpg = cv2.imencode(".jpg", img)
    jpg_bytes = encoded_jpg.tobytes()

    frame = gateway.process_live_frame_bytes(session.session_id, jpg_bytes)
    assert frame is not None
    assert frame.shape == (480, 640, 3)
    assert session.frame_count == 1

    # 3. Test Session Teardown
    gateway.close_session(session.session_id)
    with pytest.raises(KeyError):
        gateway.process_live_frame_bytes(session.session_id, jpg_bytes)
