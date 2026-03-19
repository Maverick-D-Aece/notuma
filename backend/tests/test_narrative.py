import pytest
from backend.app.services.narrative import NarrativeService

def test_extract_dialogue():
    text = 'He said, "Hello there!" She replied, "Hi!"'
    dialogues = NarrativeService.extract_dialogue(text)
    assert len(dialogues) == 2
    assert dialogues[0]['text'] == "Hello there!"
    assert dialogues[1]['text'] == "Hi!"

def test_extract_characters():
    text = "Alice went to the store. Bob was there."
    characters = NarrativeService.extract_characters(text)
    names = [c['name'] for c in characters]
    assert "Alice" in names
    assert "Bob" in names
