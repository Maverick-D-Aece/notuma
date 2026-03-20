from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.ingestion import IngestionService
from backend.app import models
from typing import Optional

router = APIRouter()

@router.post("/upload")
async def upload_novel(
    file: UploadFile = File(...),
    project_title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    content = await file.read()

    if file.filename.endswith('.txt'):
        text = IngestionService.parse_txt(content)
    elif file.filename.endswith('.docx'):
        text = IngestionService.parse_docx(content)
    elif file.filename.endswith('.epub'):
        text = IngestionService.parse_epub(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Create project
    title = project_title or file.filename.rsplit('.', 1)[0]
    project = models.Project(title=title, user_id=None)
    db.add(project)
    db.flush()

    chapters_data = IngestionService.split_into_chapters(text)

    for c_data in chapters_data:
        chapter = models.Chapter(
            title=c_data['title'],
            order=c_data['order'],
            project_id=project.id,
            content=c_data['content']
        )
        db.add(chapter)
        db.flush()

        scenes_data = IngestionService.split_into_scenes(c_data['content'])
        for s_data in scenes_data:
            scene = models.Scene(
                order=s_data['order'],
                chapter_id=chapter.id,
                text=s_data['text']
            )
            db.add(scene)

    db.commit()
    db.refresh(project)

    return {
        "projectId": project.id,
        "title": project.title,
        "chapters": [{"id": c.id, "title": c.title, "order": c.order} for c in project.chapters]
    }
