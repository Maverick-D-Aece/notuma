import pytest
from backend.app.services.ingestion import IngestionService

def test_split_into_chapters():
    text = "Chapter 1\nThis is content 1\nCHAPTER 2\nThis is content 2"
    chapters = IngestionService.split_into_chapters(text)
    assert len(chapters) == 2
    assert chapters[0]['title'] == "Chapter 1"
    assert chapters[1]['title'] == "CHAPTER 2"

def test_split_into_scenes():
    content = "Scene 1\n***\nScene 2\n###\nScene 3"
    scenes = IngestionService.split_into_scenes(content)
    assert len(scenes) == 3
    assert "Scene 1" in scenes[0]['text']
    assert "Scene 2" in scenes[1]['text']
    assert "Scene 3" in scenes[2]['text']
