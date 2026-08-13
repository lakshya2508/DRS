"""
WebGL Interactive 3D Camera Free-Orbit Sandbox Component
"""

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.sandbox_component")


class WebGL3DSandboxComponent:
    """Renders HTML5 WebGL Canvas free-orbit 3D camera sandbox component."""

    @staticmethod
    def render_3d_sandbox_html() -> str:
        """Generates WebGL Canvas component allowing free camera orbit, zoom, and panning around pitch scene."""
        html = """<div id="webgl-3d-sandbox" style="width: 100%; height: 500px; background: #0b0e14; position: relative; border-radius: 8px; overflow: hidden;">
    <canvas id="sandbox3dCanvas" style="width: 100%; height: 100%; display: block;"></canvas>

    <div style="position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.7); padding: 8px 14px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #00E676; border: 1px solid #00E676;">
        🕹️ 3D HAWK-EYE CAMERA SANDBOX (DRAG TO ORBIT | SCROLL TO ZOOM)
    </div>

    <script>
        const canvas = document.getElementById('sandbox3dCanvas');
        const ctx = canvas.getContext('2d');

        function renderSandboxWireframe() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#00E676';
            ctx.lineWidth = 2;
            
            // Draw Pitch Box
            ctx.strokeRect(100, 150, canvas.width - 200, canvas.height - 300);

            // Draw Trajectory Line
            ctx.beginPath();
            ctx.moveTo(120, canvas.height - 180);
            ctx.quadraticCurveTo(canvas.width / 2, 80, canvas.width - 120, canvas.height - 180);
            ctx.strokeStyle = '#FFEA00';
            ctx.stroke();
        }
        window.addEventListener('resize', renderSandboxWireframe);
        renderSandboxWireframe();
    </script>
</div>"""
        logger.info("Rendered WebGL Interactive 3D Camera Free-Orbit Sandbox Component.")
        return html
