import re
import nltk
from typing import List, Dict, Any

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('maxent_ne_chunker_tab')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('words')

class NarrativeService:
    @staticmethod
    def extract_dialogue(scene_text: str) -> List[Dict[str, Any]]:
        # Dialogue extraction using quotation marks
        # Improved regex to handle both double and single quotes and curly quotes
        dialogue_pattern = re.compile(r'["\'\u201c\u201d\u2018\u2019](.*?)["\'\u201c\u201d\u2018\u2019]', re.DOTALL)
        dialogues = dialogue_pattern.finditer(scene_text)

        extracted_dialogue = []
        for i, match in enumerate(dialogues):
            text = match.group(1).strip()
            if text:
                extracted_dialogue.append({"text": text, "order": i+1})

        return extracted_dialogue

    @staticmethod
    def extract_characters(text: str) -> List[Dict[str, Any]]:
        # Sophisticated character extraction placeholder
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        chunks = nltk.ne_chunk(pos_tags)

        characters = set()
        for chunk in chunks:
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                name = ' '.join(c[0] for c in chunk.leaves())
                characters.add(name)

        return [{"name": name, "traits": ["extracted"]} for name in characters]

    @staticmethod
    def map_dialogue_to_characters(dialogues: List[Dict[str, Any]], scene_text: str, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Heuristic dialogue mapping placeholder
        mapped_dialogue = []
        for d in dialogues:
            idx = scene_text.find(d['text'])
            preceding_text = scene_text[:idx][-100:]

            assigned_character = None
            for char in characters:
                if char['name'] in preceding_text:
                    assigned_character = char['name']
                    break

            mapped_dialogue.append({**d, "character_name": assigned_character})

        return mapped_dialogue

    @staticmethod
    def analyze_scene(scene_text: str, project_characters: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Perform comprehensive analysis on a scene
        dialogues = NarrativeService.extract_dialogue(scene_text)

        # If no project characters yet, extract them from the scene text
        if not project_characters:
            extracted_chars = NarrativeService.extract_characters(scene_text)
            project_characters = extracted_chars

        mapped_dialogues = NarrativeService.map_dialogue_to_characters(dialogues, scene_text, project_characters)

        return {
            "dialogues": mapped_dialogues,
            "characters": project_characters,
            "description": f"Visual summary of: {scene_text[:100]}..."
        }
