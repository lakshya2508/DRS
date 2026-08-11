"""
WebRTC Smartphone Live Camera Ingestion Gateway for Real-Time AI DRS
"""

import base64
from typing import Dict, List, Optional
import uuid
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion.webrtc")


class SDPOfferSession(BaseModel):
    """Schema representing a WebRTC PeerConnection SDP session."""
    session_id: str
    camera_id: str
    sdp_offer: str
    sdp_answer: str
    is_connected: bool = True
    frame_count: int = 0


class WebRTCLiveStreamGateway:
    """Manages WebRTC PeerConnection SDP offer/answer handshakes and frame stream ingestion."""

    def __init__(self):
        self.sessions: Dict[str, SDPOfferSession] = {}

    def create_peer_connection(self, camera_id: str, sdp_offer: str) -> SDPOfferSession:
        """Handles SDP Offer from smartphone camera and returns SDP Answer."""
        session_id = f"webrtc_{uuid.uuid4().hex[:8]}"

        # Mock SDP Answer generation for WebRTC signaling
        sdp_answer = f"v=0\r\no=- {session_id} 2 IN IP4 127.0.0.1\r\ns=AI_DRS_LIVE\r\nt=0 0\r\na=sendrecv"

        session = SDPOfferSession(
            session_id=session_id,
            camera_id=camera_id,
            sdp_offer=sdp_offer,
            sdp_answer=sdp_answer,
            is_connected=True
        )
        self.sessions[session_id] = session
        logger.info(f"Established WebRTC Live Stream Session [{session_id}] for Camera [{camera_id}]")
        return session

    def process_live_frame_bytes(self, session_id: str, jpeg_bytes: bytes) -> Optional[np.ndarray]:
        """Decodes raw JPEG/WebRTC frame bytes into OpenCV BGR numpy array."""
        if session_id not in self.sessions or not self.sessions[session_id].is_connected:
            raise KeyError(f"WebRTC session '{session_id}' not found or disconnected.")

        np_arr = np.frombuffer(jpeg_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is not None:
            self.sessions[session_id].frame_count += 1
            logger.debug(f"Decoded Live WebRTC Frame {self.sessions[session_id].frame_count} for Session [{session_id}]")

        return frame

    def close_session(self, session_id: str):
        """Closes WebRTC session and frees camera stream resources."""
        if session_id in self.sessions:
            self.sessions[session_id].is_connected = False
            del self.sessions[session_id]
            logger.info(f"Closed WebRTC Live Stream Session [{session_id}]")


# Global WebRTC gateway instance
webrtc_gateway = WebRTCLiveStreamGateway()
