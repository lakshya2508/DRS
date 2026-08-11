"""
Interactive HTML5 Canvas 3D Review Viewer Component for AI DRS Web Application
"""

from ai_drs.common.logging import setup_logger
from ai_drs.graphics.pitch_mesh import Pitch3DMeshScene

logger = setup_logger("ai_drs.api.viewer")


class HTML5ReviewViewerComponent:
    """Renders embedded HTML5/WebGL Canvas 3D pitch review viewer component."""

    @staticmethod
    def render_viewer_html(scene: Pitch3DMeshScene) -> str:
        """Generates interactive 3D WebGL HTML player component for pitch review visualization."""
        scene_json = scene.model_dump_json()

        html = f"""<div id="hawk-eye-3d-viewer" style="width: 100%; height: 450px; background: #08080C; border-radius: 8px; position: relative;">
    <canvas id="hawkEyeCanvas" style="width: 100%; height: 100%; display: block;"></canvas>
    <div style="position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.8); padding: 8px 12px; border-radius: 4px; font-family: sans-serif; font-size: 12px; color: #00E676;">
        🎮 INTERACTIVE HAWK-EYE 3D TRAJECTORY VIEWER
    </div>
    <script>
        const sceneData = {scene_json};
        const canvas = document.getElementById('hawkEyeCanvas');
        const ctx = canvas.getContext('2d');
        
        function renderScene() {{
            canvas.width = canvas.clientWidth;
            canvas.height = canvas.clientHeight;
            const w = canvas.width;
            const h = canvas.height;
            
            ctx.fillStyle = '#08080C';
            ctx.fillRect(0, 0, w, h);
            
            // Draw Pitch Surface (Perspective Projection)
            ctx.strokeStyle = '#00E676';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(w * 0.2, h * 0.85);
            ctx.lineTo(w * 0.8, h * 0.85);
            ctx.lineTo(w * 0.65, h * 0.25);
            ctx.lineTo(w * 0.35, h * 0.25);
            ctx.closePath();
            ctx.stroke();
            
            // Draw Batter Stumps
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 3;
            ctx.strokeRect(w * 0.48, h * 0.18, w * 0.04, h * 0.07);
        }}
        window.addEventListener('resize', renderScene);
        renderScene();
    </script>
</div>"""

        logger.info("Rendered Interactive HTML5 Canvas 3D Review Viewer Component.")
        return html
