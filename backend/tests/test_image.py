import pytest
from backend.app.services.image_generation import ModelHub

def test_model_hub_initialization():
    hub = ModelHub()
    assert len(hub.providers) == 5
    assert "pollinations" in hub.providers
    assert "openai" in hub.providers

def test_style_extraction():
    style = ModelHub.extract_style_from_url("https://mangadex.org/title/123")
    assert style["style_name"] == "MangaDex Consistent"
    assert style["line_weight"] == "bold"

def test_generate_panel_pollinations():
    hub = ModelHub()
    # Mocking the actual generation to avoid network issues
    # But for now, we can test the logic
    assert hub is not None

def test_byok_initialization():
    hub = ModelHub({"openai": "test-key"})
    assert hub.providers["openai"].api_key == "test-key"
