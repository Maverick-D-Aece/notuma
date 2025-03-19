"""
NoTuMa - Novel to Manga Converter

A Flask-based web application that converts novels into manga format by:
1. Processing input texts (TXT, EPUB, DOCX)
2. Segmenting content into scenes
3. Generating manga-style images
4. Supporting manga panel layouts and speech bubbles
5. Exporting in manga/comic formats

Built with a local-first approach supporting both cloud and local AI models.
"""

import os
import time
import json
import uuid
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import nltk
import torch
import requests
import ebooklib
import docx
from ebooklib import epub
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from diffusers import StableDiffusionPipeline
import pollinations as ai
from nltk.tokenize import sent_tokenize

class NovelProcessor:
    """Processes novel text files in various formats (TXT, EPUB, DOCX)."""

    def __init__(self):
        # TODO document why this method is empty
        pass

    @staticmethod
    def read_novel_file(file_path: Union[str, Path]) -> str:
        """
        Read novel content from various file formats.
        
        Args:
            file_path: Path to the novel file
            
        Returns:
            Novel text content
        
        Raises:
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        elif extension == '.epub':
            return NovelProcessor._read_epub(file_path)
            
        elif extension == '.docx':
            return NovelProcessor._read_docx(file_path)
            
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def _read_epub(file_path: Union[str, Path]) -> str:
        """Read content from EPUB file."""
        book = epub.read_epub(file_path)
        text_content = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                text_content.append(soup.get_text())
                
        return '\n\n'.join(text_content)
    
    @staticmethod
    def _read_docx(file_path: Union[str, Path]) -> str:
        """Read content from DOCX file."""
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    @staticmethod
    def segment_chapters(text: str) -> List[str]:
        """
        Segment the novel text into chapters based on common chapter markers.
        
        Args:
            text: The novel text
            
        Returns:
            List of chapter texts
        """
        # Look for common chapter markers
        chapter_markers = [
            "Chapter", "CHAPTER", 
            "Part", "PART",
            "Section", "SECTION"
        ]
        
        lines = text.split('\n')
        chapters = []
        current_chapter = []
        
        for line in lines:
            if any(marker in line for marker in chapter_markers) and len(line.strip().split()) <= 5:
                if current_chapter:
                    chapters.append('\n'.join(current_chapter))
                    current_chapter = []
                current_chapter.append(line)
            else:
                current_chapter.append(line)
                
        if current_chapter:
            chapters.append('\n'.join(current_chapter))
            
        # If no chapters were detected, treat the whole text as one chapter
        if not chapters:
            chapters = [text]
            
        return chapters
    
    @staticmethod
    def segment_scenes(text: str, sentences_per_scene: int = 8) -> List[str]:
        """
        Segment text into scenes based on paragraph breaks or sentence count.
        
        Args:
            text: The novel text to segment
            sentences_per_scene: Number of sentences per scene if no natural breaks
            
        Returns:
            List of scene texts
        """
        # Try to find natural scene breaks first (double line breaks)
        paragraphs = text.split('\n\n')
        
        # If there are meaningful paragraph breaks, use those
        if len(paragraphs) > 1 and all(len(p.strip()) > 0 for p in paragraphs):
            return [p.strip() for p in paragraphs if p.strip()]
            
        # Otherwise segment by sentence count
        sentences = sent_tokenize(text)
        scenes = []
        current_scene = []

        for sentence in sentences:
            current_scene.append(sentence)
            
            if len(current_scene) >= sentences_per_scene:
                scenes.append(" ".join(current_scene))
                current_scene = []

        if current_scene:
            scenes.append(" ".join(current_scene))  # Add the last scene

        return scenes

    @staticmethod
    def extract_characters(text: str) -> List[dict]:
        """
        Extract characters from the novel text with some basic attributes.
        
        Args:
            text: The novel text
            
        Returns:
            List of character dictionaries with attributes
        """
        # This is a simple implementation - a production version would use NER
        words = text.split()
        character_candidates = [word.strip('.,?!":;()[]{}') for word in words if word and word[0].isupper()]
        
        # Count occurrences to find likely characters (frequent capitalized words)
        character_counts = {}
        for candidate in character_candidates:
            if len(candidate) > 1:  # Skip single letters
                character_counts[candidate] = character_counts.get(candidate, 0) + 1
        
        # Filter for characters that appear multiple times (heuristic)
        characters = []
        for name, count in character_counts.items():
            if count >= 3:  # Character appears at least 3 times
                character_data = {
                    "name": name,
                    "occurrences": count,
                    "id": str(uuid.uuid4())[:8]
                }
                characters.append(character_data)
        
        # Sort by occurrence count
        return sorted(characters, key=lambda x: x["occurrences"], reverse=True)[:20]

    @staticmethod
    def extract_dialogues(text: str) -> List[Dict[str, str]]:
        """
        Extract dialogues from the novel text.
        
        Args:
            text: The novel text
                
        Returns:
            List of dialogue dictionaries with speaker and text
        """
        dialogues = []
        lines = text.split('\n')
        current_dialogue = ""
        current_speaker = ""
        in_dialogue = False

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Check for speaker attribution patterns (e.g., "John: Hi there")
            if ':' in line and not line.startswith('"') and not line.startswith("'"):
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[0].strip().split()) <= 3:
                    # Likely a speaker:dialogue pattern
                    if current_dialogue and in_dialogue:
                        # Save previous dialogue if exists
                        dialogues.append({
                            "speaker": current_speaker,
                            "text": current_dialogue.strip(),
                            "id": str(uuid.uuid4())[:8]
                        })
                    
                    current_speaker = parts[0].strip()
                    current_dialogue = parts[1].strip()
                    in_dialogue = True
                    continue
            
            # Check for direct dialogue markers
            if line.startswith('"') or line.startswith("'"):
                if current_dialogue and in_dialogue:
                    # Save previous dialogue
                    dialogues.append({
                        "speaker": current_speaker,
                        "text": current_dialogue.strip(),
                        "id": str(uuid.uuid4())[:8]
                    })
                    
                current_dialogue = line
                current_speaker = "Unknown"  # Default speaker
                in_dialogue = True                
                
                if " said " in line.lower() or " asked " in line.lower() or " replied " in line.lower():
                    dialogue_parts = line.split('"', 1) if line.count('"') >= 2 else line.split("'", 1)
                    if len(dialogue_parts) > 1:
                        attribution = dialogue_parts[1].strip()
                        if attribution.startswith("said ") or attribution.startswith("asked ") or attribution.startswith("replied "):
                            current_speaker = attribution.split(" ", 1)[1].strip()
                        elif " said " in attribution or " asked " in attribution or " replied " in attribution:
                            speaker_parts = attribution.split(" said ", 1) if " said " in attribution else \
                                        attribution.split(" asked ", 1) if " asked " in attribution else \
                                        attribution.split(" replied ", 1)
                            if len(speaker_parts) > 1:
                                current_speaker = speaker_parts[0].strip()
                
            elif in_dialogue:
                current_dialogue += " " + line
                
                if (" said " in line.lower() or " asked " in line.lower() or " replied " in line.lower()) and current_speaker == "Unknown":
                    for verb in [" said ", " asked ", " replied "]:
                        if verb in line.lower():
                            parts = line.lower().split(verb, 1)
                            if len(parts) > 1 and len(parts[0].split()) <= 3:
                                current_speaker = parts[0].strip()
                                break

        # Add the last dialogue if there is one
        if current_dialogue and in_dialogue:
            dialogues.append({
                "speaker": current_speaker,
                "text": current_dialogue.strip(),
                "id": str(uuid.uuid4())[:8]
            })

        return dialogues


def generate_descriptions(scenes: List[str], style: str = "manga style") -> List[str]:
    """
    Generate image descriptions from scenes.

    Args:
        scenes: List of scene texts
        style: The art style to use for images

    Returns:
        List of image descriptions
    """
    descriptions = []

    for scene in scenes:
        # Extract key elements from the scene for better prompts
        scene_summary = scene[:2000].strip()

        # Add manga-specific style elements
        prompt = f"In {style}; detailed manga panel showing {scene_summary}..."
        descriptions.append(prompt)

    return descriptions


class ImageGenerator:
    """Handles image generation from text descriptions using various AI services."""
    
    def __init__(self, use_local_model: bool = False, model_provider: str = "pollinations"):
        """
        Initialize the image generator.
        
        Args:
            use_local_model: Whether to use local Stable Diffusion model
            model_provider: Which API provider to use ("pollinations", "stability", "openai", "replicate")
        """
        self.use_local_model = use_local_model
        self.model_provider = model_provider
        self.model = None
        
        # Initialize local model if requested
        if use_local_model:
            try:
                model_id = "CompVis/stable-diffusion-v-1-4"
                self.model = StableDiffusionPipeline.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                
                if torch.cuda.is_available():
                    self.model = self.model.to("cuda")
                    app.logger.info("Using CUDA for local image generation")
                else:
                    app.logger.warning("CUDA not available, using CPU for image generation. This will be slow.")
            except Exception as e:
                app.logger.error(f"Failed to initialize local model: {str(e)}")
                self.use_local_model = False

    def generate_image(self, description: str, width: int = 512, height: int = 512) -> Dict[str, Any]:
        """
        Generate an image from a description using the configured provider.
        
        Args:
            description: The image description prompt
            width: Image width
            height: Image height
            
        Returns:
            Dictionary with image path and metadata
        """
        app.logger.info(f"Generating image for: {description[:500]}...")
        
        # Generate a unique filename
        timestamp = int(time.time() * 1000)
        filename = f"manga_panel_{timestamp}.png"
        filepath = IMAGE_OUTPUT_DIR / filename
        
        try:
            if self.use_local_model and self.model:
                self._generate_with_local_model(description, filepath)
            else:
                if self.model_provider == "pollinations":
                    self._generate_with_pollinations(filepath, description, width, height)
                elif self.model_provider == "stability":
                    self._generate_with_stability(description, filepath, width, height)
                elif self.model_provider == "openai":
                    self._generate_with_openai(description, filepath, width, height)
                elif self.model_provider == "replicate":
                    self._generate_with_replicate(description, filepath, width, height)
                else:
                    raise ValueError(f"Unknown model provider: {self.model_provider}")
            
            return {
                "path": f"/static/generated_images/{filename}",
                "filename": filename,
                "description": description[:100],
                "timestamp": timestamp,
                "width": width,
                "height": height
            }
        except Exception as e:
            app.logger.error(f"Error generating image: {str(e)}")
            return {
                "path": "/static/error_image.png",
                "error": str(e),
                "description": description[:100]
            }
    
    def _generate_with_local_model(self, prompt: str, filepath: Path) -> None:
        """Generate image using local Stable Diffusion model."""
        with torch.no_grad():
            image = self.model(prompt).images[0]
            image.save(filepath)
    
    def _generate_with_pollinations(
        self, 
        filepath: Path,
        prompt: str, 
        width: int = 512, 
        height: int = 512, 
        seed: int = 1290166404
    ) -> str:
        """Generate image using Pollinations.ai API."""
        image_model = ai.Image(
            model=ai.Image.flux(),
            seed=seed,
            width=width,
            height=height,
            enhance=False,
            nologo=True,
            private=True,
            safe=False,
            referrer="pollinations.py"
        ) 
        image = image_model(
            prompt=prompt
        )
        app.logger.info(f'Image generation response: {image.response}')
        image.save(filepath)
    
    def _generate_with_stability(self, prompt: str, filepath: Path, width: int, height: int) -> None:
        """Generate image using Stability.ai API."""
        if not STABILITY_API_KEY:
            raise ValueError("STABILITY_API_KEY is not set in environment variables")
            
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        }
        
        body = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        image_data = data["artifacts"][0]["base64"]
        
        image = Image.open(BytesIO(b64decode(image_data)))
        image.save(filepath)
    
    def _generate_with_openai(self, prompt: str, filepath: Path, width: int, height: int) -> None:
        """Generate image using OpenAI's DALL-E API."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
            
        import openai
        openai.api_key = OPENAI_API_KEY
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=f"{width}x{height}"
        )
        
        image_url = response["data"][0]["url"]
        self._download_image(image_url, filepath)
    
    def _generate_with_replicate(self, prompt: str, filepath: Path, width: int, height: int) -> None:
        """Generate image using Replicate's API."""
        if not REPLICATE_API_KEY:
            raise ValueError("REPLICATE_API_KEY is not set in environment variables")
            
        import replicate
        client = replicate.Client(api_token=REPLICATE_API_KEY)
        
        output = client.run(
            "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316",
            input={
                "prompt": prompt,
                "width": width,
                "height": height
            }
        )
        
        if output and isinstance(output, list) and len(output) > 0:
            image_url = output[0]
            self._download_image(image_url, filepath)
        else:
            raise ValueError("Failed to generate image with Replicate")
    
    @staticmethod
    def _download_image(url: str, filepath: Union[str, Path]) -> None:
        """
        Download an image from a URL.
        
        Args:
            url: The image URL
            filepath: Where to save the image
        """
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with open(filepath, 'wb') as file:
            file.write(response.content)
        app.logger.debug(f'Image downloaded to {filepath}')


# Initialize services
novel_processor = NovelProcessor()
image_generator = ImageGenerator()

# Ensure NLTK dependencies are downloaded
nltk.download('punkt', quiet=True)

# Initialize environment variables
load_dotenv('keys.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

# Application directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
IMAGE_OUTPUT_DIR = STATIC_DIR / "generated_images"
MANGA_OUTPUT_DIR = STATIC_DIR / "manga_exports"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, IMAGE_OUTPUT_DIR, MANGA_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size


class MangaLayoutEngine:
    """Handles manga panel layout and composition."""
    
    PANEL_TEMPLATES = {
        "standard_2x2": [
            {"x": 0, "y": 0, "width": 0.5, "height": 0.5},
            {"x": 0.5, "y": 0, "width": 0.5, "height": 0.5},
            {"x": 0, "y": 0.5, "width": 0.5, "height": 0.5},
            {"x": 0.5, "y": 0.5, "width": 0.5, "height": 0.5}
        ],
        "wide_top_2_bottom": [
            {"x": 0, "y": 0, "width": 1.0, "height": 0.5},
            {"x": 0, "y": 0.5, "width": 0.5, "height": 0.5},
            {"x": 0.5, "y": 0.5, "width": 0.5, "height": 0.5}
        ],
        "dynamic_3_panel": [
            {"x": 0, "y": 0, "width": 0.6, "height": 0.7},
            {"x": 0.6, "y": 0, "width": 0.4, "height": 0.4},
            {"x": 0.6, "y": 0.4, "width": 0.4, "height": 0.6}
        ],
        "manga_action": [
            {"x": 0, "y": 0, "width": 0.7, "height": 0.6},
            {"x": 0.7, "y": 0, "width": 0.3, "height": 0.3},
            {"x": 0.7, "y": 0.3, "width": 0.3, "height": 0.3},
            {"x": 0, "y": 0.6, "width": 1.0, "height": 0.4}
        ]
    }
    
    @staticmethod
    def create_manga_page(
        images: List[Dict[str, Any]], 
        dialogues: List[Dict[str, str]], 
        template_name: str = "standard_2x2",
        page_width: int = 800,
        page_height: int = 1200,
        border_color: str = "black",
        border_width: int = 3,
        rtl: bool = True  # Right-to-Left reading for manga
    ) -> Tuple[Image.Image, str]:
        """
        Create a manga page with panels and speech bubbles.
        
        Args:
            images: List of image metadata with paths
            dialogues: List of dialogue texts to add
            template_name: Name of panel template to use
            page_width: Page width in pixels
            page_height: Page height in pixels
            border_color: Panel border color
            border_width: Panel border width
            rtl: Whether to use right-to-left panel ordering
            
        Returns:
            Tuple of (PIL Image, output filepath)
        """
        # Create blank white page
        page = Image.new('RGB', (page_width, page_height), 'white')
        draw = ImageDraw.Draw(page)
        
        # Get panel template or use default
        template = MangaLayoutEngine.PANEL_TEMPLATES.get(
            template_name, 
            MangaLayoutEngine.PANEL_TEMPLATES["standard_2x2"]
        )
        
        panel_count = min(len(template), len(images))
        
        # Sort panels based on reading direction
        panel_indices = list(range(panel_count))
        if rtl:
            # For right-to-left (manga style), we reverse the horizontal order
            # This is a simplified approach; real manga layout would be more complex
            panel_indices.reverse()
        
        # Place images into panels
        for i in range(panel_count):
            panel_idx = panel_indices[i]
            panel = template[i]
            image_data = images[panel_idx]
            
            # Calculate panel position and size
            x = int(panel["x"] * page_width)
            y = int(panel["y"] * page_height)
            width = int(panel["width"] * page_width)
            height = int(panel["height"] * page_height)
            
            # Load and resize image to fit panel
            image_path = BASE_DIR / image_data["path"].lstrip('/')
            try:
                img = Image.open(image_path)
                img = img.resize((width, height), Image.LANCZOS)
                
                # Paste image onto page
                page.paste(img, (x, y))
                
                # Draw panel border
                draw.rectangle(
                    [(x, y), (x + width, y + height)], 
                    outline=border_color, 
                    width=border_width
                )
                
                # Add speech bubble if dialogue exists for this panel
                if i < len(dialogues):
                    dialogue = dialogues[i]
                    MangaLayoutEngine.add_speech_bubble(
                        page, 
                        draw, 
                        dialogue["text"], 
                        (x + width//4, y + height//4),
                        width//2, 
                        height//3
                    )
            except Exception as e:
                app.logger.error(f"Error placing image in panel: {str(e)}")
        
        # Save the page
        timestamp = int(time.time())
        output_filename = f"manga_page_{timestamp}.png"
        output_path = MANGA_OUTPUT_DIR / output_filename
        page.save(output_path)
        
        return page, str(output_path)
    
    @staticmethod
    def add_speech_bubble(
        image: Image.Image, 
        draw: ImageDraw.Draw, 
        text: str, 
        position: Tuple[int, int],
        width: int, 
        height: int,
        bubble_color: str = "white",
        text_color: str = "black",
        bubble_type: str = "round"  # "round", "thought", "angular"
    ) -> None:
        """
        Add a speech bubble to the image.
        
        Args:
            image: PIL Image to draw on
            draw: ImageDraw object
            text: Text to add to bubble
            position: (x, y) position for bubble
            width: Max width of bubble
            height: Max height of bubble
            bubble_color: Fill color for bubble
            text_color: Text color
            bubble_type: Type of speech bubble
        """
        x, y = position
        
        # Adjust bubble shape based on type
        if bubble_type == "round":
            # Standard speech bubble
            draw.ellipse([x-10, y-10, x+width+10, y+height+10], fill=bubble_color, outline="black")
            # Add tail
            points = [(x+width//4, y+height+10), (x+width//3, y+height+30), (x+width//2, y+height+10)]
            draw.polygon(points, fill=bubble_color, outline="black")
        elif bubble_type == "thought":
            # Thought bubble - main bubble
            draw.ellipse([x-10, y-10, x+width+10, y+height+10], fill=bubble_color, outline="black")
            # Thought circles
            for i in range(3):
                size = 10 - i*2
                draw.ellipse(
                    [x+width//2-size, y+height+10+i*7, x+width//2+size, y+height+10+i*7+size*2], 
                    fill=bubble_color, 
                    outline="black"
                )
        elif bubble_type == "angular":
            # Angular speech bubble (for shouting/emphasis)
            points = [
                (x-10, y-10), (x+width+10, y-10), 
                (x+width+10, y+height+10), (x+width//3, y+height+10),
                (x+width//4, y+height+30), (x+width//5, y+height+10),
                (x-10, y+height+10)
            ]
            draw.polygon(points, fill=bubble_color, outline="black")
        
        # Add text (simplified - would need proper text wrapping in production)
        try:
            # Try to load a manga-style font if available
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Simple text wrapping
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Check if adding this word would exceed the width
            test_width = draw.textlength(test_line, font=font)
            
            if test_width <= width - 20:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line of text
        for i, line in enumerate(lines[:5]):  # Limit to 5 lines
            draw.text(
                (x + 10, y + 10 + i*20), 
                line, 
                fill=text_color, 
                font=font
            )


class MangaExporter:
    """Handles exporting manga pages to various formats."""
    
    @staticmethod
    def export_to_cbz(page_paths: List[str], title: str = "manga_export") -> str:
        """
        Export manga pages to CBZ format.
        
        Args:
            page_paths: List of paths to page images
            title: Title for the CBZ file
            
        Returns:
            Path to the exported CBZ file
        """
        import zipfile
        
        # Create filename with timestamp
        timestamp = int(time.time())
        cbz_filename = f"{title}_{timestamp}.cbz"
        cbz_path = MANGA_OUTPUT_DIR / cbz_filename
        
        # Create CBZ file (which is just a ZIP with images)
        with zipfile.ZipFile(cbz_path, 'w') as cbz:
            for i, page_path in enumerate(page_paths):
                # Add page to archive with sequential numbering
                page_name = f"page_{i+1:03d}.png"
                cbz.write(page_path, arcname=page_name)
        
        return str(cbz_path)
    
    @staticmethod
    def export_to_pdf(page_paths: List[str], title: str = "manga_export") -> str:
        """
        Export manga pages to PDF format.
        
        Args:
            page_paths: List of paths to page images
            title: Title for the PDF file
            
        Returns:
            Path to the exported PDF file
        """
        from PIL import Image
        
        # Create filename with timestamp
        timestamp = int(time.time())
        pdf_filename = f"{title}_{timestamp}.pdf"
        pdf_path = MANGA_OUTPUT_DIR / pdf_filename
        
        # Open all images
        images = []
        for page_path in page_paths:
            try:
                images.append(Image.open(page_path).convert('RGB'))
            except Exception as e:
                app.logger.error(f"Error loading image for PDF: {str(e)}")
        
        if images:
            # Save as PDF
            images[0].save(
                pdf_path, 
                save_all=True, 
                append_images=images[1:],
                resolution=100.0,
                quality=95
            )
        
        return str(pdf_path)



@app.route('/')
def index():
    """Render the main NoTuMa application page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_novel():
    """Handle novel file upload and initial processing."""
    try:
        # Check if a file was uploaded
        if 'novelFile' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['novelFile']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save the uploaded file
        filename = f"{int(time.time())}_{file.filename}"
        file_path = UPLOAD_DIR / filename
        file.save(file_path)
        
        # Process the novel file
        try:
            novel_text = novel_processor.read_novel_file(file_path)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Extract core content
        chapters = novel_processor.segment_chapters(novel_text)
        
        return jsonify({
            "success": True,
            "message": "Novel uploaded successfully",
            "fileId": filename,
            "chapterCount": len(chapters),
            "wordCount": len(novel_text.split()),
            "chapters": [{"id": i, "title": c[:50] + "..." if len(c) > 50 else c} for i, c in enumerate(chapters)]
        })
        
    except Exception as e:
        app.logger.error(f"Error uploading novel: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/process_chapter', methods=['POST'])
def process_chapter():
    """Process a single chapter into scenes and extract key information."""
    try:
        data = request.get_json()
        if not data or 'fileId' not in data or 'chapterId' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        file_id = data['fileId']
        chapter_id = int(data['chapterId'])
        
        # Load the novel file
        file_path = UPLOAD_DIR / file_id
        novel_text = novel_processor.read_novel_file(file_path)
        
        # Get chapters and select the requested one
        chapters = novel_processor.segment_chapters(novel_text)
        if chapter_id >= len(chapters):
            return jsonify({"error": "Chapter index out of range"}), 400
            
        chapter_text = chapters[chapter_id]
        
        # Process chapter into scenes
        scenes_per_page = data.get('scenesPerPage', 4)
        scenes = novel_processor.segment_scenes(chapter_text, sentences_per_scene=8)
        
        # Extract characters and dialogues
        characters = novel_processor.extract_characters(chapter_text)
        dialogues = novel_processor.extract_dialogues(chapter_text)
        
        # Generate scene descriptions for image prompts
        style = data.get('mangaStyle', 'manga style')
        descriptions = generate_descriptions(scenes, style=style)
        
        return jsonify({
            "success": True,
            "chapterTitle": chapter_text[:50] + "..." if len(chapter_text) > 50 else chapter_text,
            "sceneCount": len(scenes),
            "scenes": [{"id": i, "text": s[:100] + "..." if len(s) > 100 else s, 
                        "description": descriptions[i]} 
                      for i, s in enumerate(scenes)],
            "characters": characters[:10],  # Limit to top 10 characters
            "dialogues": dialogues[:20]  # Limit to 20 most relevant dialogues
        })
        
    except Exception as e:
        app.logger.error(f"Error processing chapter: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/generate_images', methods=['POST'])
def generate_images():
    """Generate images for selected scenes."""
    try:
        data = request.get_json()
        if not data or 'descriptions' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        descriptions = data['descriptions']
        width = data.get('width', 512)
        height = data.get('height', 512)
        
        # Generate images for each description
        generated_images = []
        for desc in descriptions:
            image_data = image_generator.generate_image(desc, width, height)
            generated_images.append(image_data)
            
        return jsonify({
            "success": True,
            "images": generated_images,
            "nextTabEnabled": True  # Enable the next tab button
        })
        
    except Exception as e:
        app.logger.error(f"Error generating images: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/create_manga_page', methods=['POST'])
def create_manga_page():
    """Create a manga page with selected images and dialogues."""
    try:
        data = request.get_json()
        print("data: ", data)
        if not data or 'images' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        images = data['images']
        dialogues = data.get('dialogues', [])
        
        # Get layout settings
        template = data.get('templateName', 'standard_2x2')
        page_width = data.get('width', 800)
        page_height = data.get('height', 800)
        border_color = data.get('borderColor', 'black')
        border_width = data.get('borderWidth', 4)
        rtl = data.get('rightToLeft', True)
        
        # Create the manga page
        _, output_path = MangaLayoutEngine.create_manga_page(
            images=images,
            dialogues=dialogues,
            template_name=template,
            page_width=page_width,
            page_height=page_height,
            border_color=border_color,
            border_width=border_width,
            rtl=rtl
        )
        
        # Get relative path for response
        rel_path = str(output_path).replace(str(BASE_DIR), '')
        if rel_path.startswith('/'):
            rel_path = rel_path[1:]
            
        return jsonify({
            "success": True,
            "pagePath": f"/static/{rel_path.split('static/')[1]}"
        })
        
    except Exception as e:
        app.logger.error(f"Error creating manga page: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/export_manga', methods=['POST'])
def export_manga():
    """Export manga pages to a selected format."""
    try:
        data = request.get_json()
        if not data or 'pages' not in data or 'format' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        pages = data['pages']
        export_format = data['format'].lower()
        title = data.get('title', 'manga_export')
        
        # Validate page paths
        page_paths = []
        for page in pages:
            path = page.get('pagePath', '').lstrip('/')
            full_path = BASE_DIR / path
            if full_path.exists():
                page_paths.append(str(full_path))
            else:
                app.logger.warning(f"Page not found: {full_path}")
        
        if not page_paths:
            return jsonify({"error": "No valid pages found"}), 400
            
        # Export based on format
        if export_format == 'cbz':
            output_path = MangaExporter.export_to_cbz(page_paths, title)
        elif export_format == 'pdf':
            output_path = MangaExporter.export_to_pdf(page_paths, title)
        else:
            return jsonify({"error": f"Unsupported export format: {export_format}"}), 400
        
        # Get relative path for response
        rel_path = str(output_path).replace(str(BASE_DIR), '')
        if rel_path.startswith('/'):
            rel_path = rel_path[1:]
            
        return jsonify({
            "success": True,
            "exportPath": f"/static/{rel_path.split('static/')[1]}",
            "format": export_format
        })
        
    except Exception as e:
        app.logger.error(f"Error exporting manga: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a generated file."""
    try:
        # Check if file exists in MANGA_OUTPUT_DIR
        file_path = MANGA_OUTPUT_DIR / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Missing imports from the provided code
from base64 import b64decode

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)