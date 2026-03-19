# NoTuMa GitHub Project Roadmap

## Epic 1: Scaffold Anew & Core Infrastructure
*   **Issue 1.1:** Setup Next.js (App Router) with Tailwind CSS & Lucide React.
*   **Issue 1.2:** Initialize FastAPI backend with core API structure.
*   **Issue 1.3:** Configure PostgreSQL with Prisma/SQLAlchemy and database migrations.
*   **Issue 1.4:** Integrate S3-compatible storage (Cloudflare R2/AWS S3) for assets.
*   **Issue 1.5:** Implement robust authentication (Auth.js or Clerk).

## Epic 2: Intelligent Narrative Analysis (NLP)
*   **Issue 2.1:** Develop a sophisticated text parser for EPUB, DOCX, and TXT with chapter/scene splitting.
*   **Issue 2.2:** Integrate an LLM-based character extraction engine (detecting physical traits and relationships).
*   **Issue 2.3:** Implement dialogue-to-character mapping using context-aware NLP.
*   **Issue 2.4:** Build a "Narrative Scene" editor for users to manually adjust extracted scenes/dialogue.

## Epic 3: High-Fidelity Image Generation
*   **Issue 3.1:** Create a modular "Model Hub" for multiple AI providers (Pollinations, Stability, OpenAI).
*   **Issue 3.2:** Implement **BYOK (Bring Your Own Key)** support for NanoBanana and Replicate.
*   **Issue 3.3:** Add **Style Transfer** support: Analyze MangaDex links/images for style consistency.
*   **Issue 3.4:** Develop "Character Presets" to maintain visual consistency across panels using LoRAs or IP-Adapter.

## Epic 4: Professional Manga/Manhwa Composition Engine
*   **Issue 4.1:** Build a canvas-based layout editor (supporting diagonal and overlapping panels).
*   **Issue 4.2:** Add **Manhwa Style** support: Long-strip vertical scrolling layouts.
*   **Issue 4.3:** Implement advanced speech bubbles (custom fonts, dynamic tails, and manga-style emphasis).
*   **Issue 4.4:** Support for screentones, speed lines, and manga textures as post-processing layers.

## Epic 5: Advanced Exports
*   **Issue 5.1:** Implement high-resolution PNG/JPEG exports per page.
*   **Issue 5.2:** Develop a **Fixed-Layout EPUB** export pipeline.
*   **Issue 5.3:** Create CBZ (Comic Book Archive) and PDF packaging workers.
*   **Issue 5.4:** Implement batch export for entire chapters/volumes.

## Epic 6: DevOps & Scaling (Final Step)
*   **Issue 6.1:** Dockerize all services (Frontend, Backend, Worker, Redis).
*   **Issue 6.2:** Setup CI/CD pipeline for automated testing and deployment.
*   **Issue 6.3:** Configure monitoring and error tracking (Sentry/New Relic).
*   **Issue 6.4:** Implement rate limiting and cost-usage tracking for AI API keys.
