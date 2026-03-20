from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.narrative import NarrativeService
from backend.app import models

router = APIRouter()

@router.get("/chapter/{chapterId}")
def get_chapter_analysis(chapterId: str, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapterId).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    project = chapter.project
    project_characters = [{"id": c.id, "name": c.name} for c in project.characters]

    analyzed_scenes = []
    # Use characters from the whole project or dynamic extraction
    all_known_characters = project_characters.copy()

    for scene in chapter.scenes:
        analysis = NarrativeService.analyze_scene(scene.text, all_known_characters)

        # Merge dynamically discovered characters
        for char in analysis['characters']:
            if not any(c['name'] == char['name'] for c in all_known_characters):
                # Optionally auto-add to project here, or keep for UI to confirm
                all_known_characters.append({"id": None, "name": char['name']})

        analyzed_scenes.append({
            "id": scene.id,
            "text": scene.text,
            "order": scene.order,
            "dialogue": analysis['dialogues'],
            "description": analysis['description']
        })

    return {
        "id": chapter.id,
        "title": chapter.title,
        "scenes": analyzed_scenes,
        "characters": all_known_characters
    }

@router.post("/character/profile")
def update_character_profile(
    projectId: str,
    name: str,
    traits: list[str],
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == projectId).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    character = models.Character(
        name=name,
        traits=traits,
        project_id=projectId
    )
    db.add(character)
    db.commit()
    db.refresh(character)

    return {"id": character.id, "name": character.name, "traits": character.traits}
