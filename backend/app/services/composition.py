from PIL import Image, ImageDraw, ImageFont
import json
from typing import Dict, Any, List
import io

class CompositionService:
    def __init__(self):
        # Default canvas size for manga (1200x1800)
        self.default_width = 1200
        self.default_height = 1800

    def render_page(self, layout_data: Dict[str, Any], is_manhwa: bool = False, img_format: str = 'PNG', scale: float = 1.0) -> io.BytesIO:
        """
        Renders a manga/manhwa page based on layout data.
        """
        width = int(layout_data.get("width", self.default_width) * scale)
        height = int(layout_data.get("height", self.default_height) * scale)

        # Create a blank white canvas
        canvas = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # 1. Render Panels (Issue 4.1)
        for panel in layout_data.get("panels", []):
            self._render_panel(canvas, panel, scale)

        # 2. Apply Manga Effects (Issue 4.4)
        for effect in layout_data.get("effects", []):
            self._apply_effect(canvas, effect, scale)

        # 3. Render Speech Bubbles (Issue 4.3)
        for bubble in layout_data.get("bubbles", []):
            self._render_bubble(canvas, bubble, scale)

        # Save to buffer
        img_byte_arr = io.BytesIO()
        # Ensure we use the requested format
        save_format = 'JPEG' if img_format.upper() in ['JPG', 'JPEG'] else 'PNG'
        canvas.save(img_byte_arr, format=save_format)
        img_byte_arr.seek(0)
        return img_byte_arr

    def _render_panel(self, canvas: Image.Image, panel_data: Dict[str, Any], scale: float = 1.0):
        """Renders a panel onto the canvas, supporting clipping and positioning."""
        # In a real app, we'd fetch the image from S3 and resize/clip it
        pass

    def _render_bubble(self, canvas: Image.Image, bubble_data: Dict[str, Any], scale: float = 1.0):
        """Renders advanced speech bubbles (Issue 4.3)."""
        draw = ImageDraw.Draw(canvas)
        text = bubble_data.get("text", "")
        x = int(bubble_data.get("x", 0) * scale)
        y = int(bubble_data.get("y", 0) * scale)
        w = int(150 * scale)
        h = int(100 * scale)

        # Simple elliptical bubble for demonstration
        draw.ellipse([x, y, x + w, y + h], fill="white", outline="black", width=max(1, int(2 * scale)))
        # In a real app, we'd use a proper font and handle text wrapping
        draw.text((x + int(20 * scale), y + int(30 * scale)), text, fill="black")

    def _apply_effect(self, canvas: Image.Image, effect_data: Dict[str, Any], scale: float = 1.0):
        """Applies manga textures like screentones or speed lines (Issue 4.4)."""
        pass

    def create_manhwa_strip(self, pages: List[Dict[str, Any]], scale: float = 1.0) -> io.BytesIO:
        """Combines multiple pages into a long vertical strip (Issue 4.2)."""
        rendered_pages = []
        total_height = 0
        max_width = 0

        for page_layout in pages:
            img_buffer = self.render_page(page_layout, is_manhwa=True, scale=scale)
            img = Image.open(img_buffer)
            rendered_pages.append(img)
            total_height += img.height
            max_width = max(max_width, img.width)

        strip = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))
        current_y = 0
        for img in rendered_pages:
            strip.paste(img, (0, current_y))
            current_y += img.height

        img_byte_arr = io.BytesIO()
        strip.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
