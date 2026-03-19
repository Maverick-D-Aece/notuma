# API Specification

The NoTuMa API is a RESTful service built with FastAPI. It provides the endpoints for narrative analysis, image generation, and manga composition.

## Endpoint Overview

### 1. Ingestion & Narrative Analysis

#### POST /api/v1/ingest/upload
Uploads a novel file and returns the chapter/scene segmentation.
-   **Body:** `multipart/form-data` (file: File)
-   **Returns:** `{ "projectId": String, "chapters": [{ "id": String, "title": String, "wordCount": Int }] }`

#### GET /api/v1/narrative/chapter/{chapterId}
Fetches a detailed analysis of a chapter, including scenes and characters.
-   **Returns:** `{ "scenes": [{ "id": String, "text": String, "dialogue": [{ "characterId": String, "text": String }] }], "characters": [{ "id": String, "name": String, "traits": String[] }] }`

#### POST /api/v1/narrative/character/profile
Updates or creates a character profile with visual traits.
-   **Body:** `{ "projectId": String, "name": String, "traits": String[], "visualRefUrl": String? }`

### 2. Image Generation & Model Hub

#### POST /api/v1/image/generate
Enqueues a task to generate an image panel for a specific scene.
-   **Body:** `{ "sceneId": String, "prompt": String, "styleProfileId": String?, "provider": String? }`
-   **Returns:** `{ "taskId": String, "status": "pending" | "processing" | "completed" }`

#### GET /api/v1/image/status/{taskId}
Checks the status of a generation task.
-   **Returns:** `{ "taskId": String, "status": "completed", "imageUrl": String? }`

#### GET /api/v1/model-hub/providers
Returns a list of available AI providers and their configuration requirements (e.g., BYOK).
-   **Returns:** `[{ "id": String, "name": String, "requiresApiKey": Boolean, "capabilities": String[] }]`

### 3. Composition & Canvas Editor

#### GET /api/v1/composition/page/{pageId}
Fetches the layout data for a manga page.
-   **Returns:** `{ "pageId": String, "layout": Json, "imageUrl": String? }`

#### POST /api/v1/composition/page/save
Saves the current canvas layout for a page.
-   **Body:** `{ "pageId": String, "layout": Json }`

#### POST /api/v1/composition/page/render
Renders a high-resolution version of the manga page based on the current layout.
-   **Body:** `{ "pageId": String }`
-   **Returns:** `{ "taskId": String }`

### 4. Project Management & Export

#### GET /api/v1/project/{projectId}
Fetches all metadata and assets for a project.
-   **Returns:** `{ "id": String, "title": String, "chapters": Chapter[], "characters": Character[] }`

#### POST /api/v1/project/export
Enqueues a task to export a project or chapter in the requested format (PDF, CBZ, EPUB).
-   **Body:** `{ "projectId": String, "chapterId": String?, "format": "pdf" | "cbz" | "epub" }`
-   **Returns:** `{ "taskId": String }`

#### GET /api/v1/project/export/{taskId}
Checks the status and returns the download link for an export.
-   **Returns:** `{ "taskId": String, "status": "completed", "downloadUrl": String? }`
