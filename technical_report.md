# NoTuMa Technical Assessment & Future Roadmap

## 1. Executive Summary
NoTuMa (Novel To Manga) is currently a proof-of-concept application built on a "boring" and monolithic stack (Flask/Vanilla JS). While it demonstrates the core workflow of converting text to panels, the implementation is fragile, lacks professional manga aesthetics, and has reached its scalability limit. This report outlines the current technical debt and proposes a complete architectural "scaffold anew" to transform NoTuMa into a high-fidelity, professional-grade manga production tool.

## 2. Current State Analysis

### 2.1 Narrative Analysis (NLP)
*   **Heuristic Extraction:** Currently uses basic NLTK tokenization and uppercase word counting for character detection. This leads to high noise and misses nuanced character interactions.
*   **Dialogue Mapping:** Fails to accurately map dialogue to specific scenes or characters, resulting in disjointed speech bubbles.
*   **Scene Segmentation:** Relies on arbitrary sentence counts or double line breaks, often breaking narrative flow.

### 2.2 Image Generation
*   **Style Inconsistency:** Limited control over art style; lacks support for LoRAs, ControlNet, or style transfer from external links (e.g., MangaDex).
*   **Provider Constraints:** Hardcoded integrations for a few providers; no support for emerging high-performance models like NanoBanana.
*   **Resolution:** Limited to standard square/rectangular outputs without consideration for vertical Manhwa formats.

### 2.3 Layout & Composition
*   **Rudimentary Templates:** Hardcoded grid layouts that do not allow for dynamic, overlapping, or diagonal manga panels.
*   **Speech Bubbles:** Primitive PIL-based drawing with poor text wrapping and no font customization.
*   **Lack of Interactivity:** Users cannot manually adjust panel positions or bubble tails in the current UI.

### 2.4 Infrastructure & Persistence
*   **No Database:** All state is handled in the browser memory (client-side) or local files. Reloading the page loses all progress.
*   **File-Based Storage:** Images and novels are stored on the local server disk, which is not scalable for cloud deployment.
*   **Monolithic Backend:** Flask is acting as both a file server, API, and image processing worker, leading to performance bottlenecks.

## 3. The "Scaffold Anew" Architecture

### 3.1 Proposed Tech Stack
*   **Frontend:** **Next.js (App Router)** + **Tailwind CSS** + **Lucide React**. (Industry standard, high performance, excellent community support).
*   **Backend:** **FastAPI (Python)**. (High performance, native async support for AI processing).
*   **Database:** **PostgreSQL** with **Prisma ORM**. (Robust relational data for projects, chapters, and characters).
*   **Task Queue:** **Celery + Redis**. (Essential for long-running image generation tasks).
*   **Storage:** **AWS S3 / Cloudflare R2**. (Scalable image hosting).
*   **Editor:** **Fabric.js / Konva.js**. (Canvas-based interactive editor for panels and bubbles).

### 3.2 Key Innovations
*   **Manhwa Support:** Native support for long-strip vertical layouts with seamless transitions.
*   **Style Transfer:** Ability to ingest a MangaDex link to extract visual style parameters (color palette, line weight, screentone density).
*   **BYOK (NanoBanana):** A modular "Model Hub" allowing users to provide their own API keys for NanoBanana and other cutting-edge providers.
*   **Fixed-Layout EPUB:** Professional export pipeline for digital e-readers.


## 4. The New Architecture: Deep Dive

### 4.1 Data & Storage Layer
*   **PostgreSQL:** Handles relational metadata:
    *   **User/Project:** Root of the workspace.
    *   **Chapter/Scene:** Narrative segments with dialogue associations.
    *   **Character Profiles:** Persistent metadata (hair color, gender, age) for consistent image generation.
    *   **Style Profiles:** Extracted features from user-provided MangaDex links.
*   **Redis:** For task state tracking and scene-level caching.
*   **S3/R2:** Stores raw uploads, generated panels, and final exports.

### 4.2 Application Layers
*   **Ingestion:** Python-based parsers (EPUB, PDF, DOCX) to clean and normalize text.
*   **Inference Orchestrator:**
    *   Standardizes prompts for different providers.
    *   Handles **BYOK (Bring Your Own Key)** for NanoBanana, OpenAI, etc.
    *   Manages ControlNet/LoRA inputs for consistent character design.
*   **Composition Engine:**
    *   Client-side canvas for interactive layout.
    *   Server-side rendering (Python/Pillow) for high-resolution exports.
*   **Exporter:** Separate worker to package CBZ, PDF, and Fixed-Layout EPUB files.

### 4.3 Deployment Strategy (Final Epic)
*   **Dockerized Services:** Frontend, Backend, and Worker nodes in separate containers.
*   **CI/CD:** Automated testing for NLP parsers and export validators.
*   **Serverless Options:** Using Vercel for the Next.js frontend and AWS Lambda for lightweight ingestion tasks.
