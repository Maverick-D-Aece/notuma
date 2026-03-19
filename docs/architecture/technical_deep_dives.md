# Technical Deep Dives

This document provides more detailed information on key components and processes within NoTuMa.

## 1. NLP Pipeline for Narrative Analysis

NoTuMa's narrative engine transitions from simple heuristics to more sophisticated, context-aware analysis.

### Character & Dialogue Extraction
1.  **Preprocessing:** Text is cleaned, normalized, and segmented into chapters.
2.  **NER (Named Entity Recognition):** The engine uses advanced NLP libraries (like Spacy or specialized LLM-based extraction) to identify character names and physical traits.
3.  **Trait Synthesis:** Extracted physical traits are synthesized into character profiles.
4.  **Dialogue Attribution:** Dialogue is attributed to specific characters using context-aware mapping, tracking the "speaker" throughout a scene or chapter.
5.  **Scene Breakdown:** Chapters are segmented into narrative scenes based on character presence, location changes, and dialogue density.

## 2. Model Hub & Image Generation

The "Model Hub" is a modular interface for managing image generation requests across multiple providers.

### Architecture
-   **Provider Interface:** A standardized interface for different AI providers (Stability, OpenAI, NanoBanana, Replicate, Pollinations).
-   **Prompt Orchestrator:** Generates optimal prompts for each provider, incorporating character profiles, style parameters, and scene descriptions.
-   **BYOK (Bring Your Own Key):** Users can provide their own API keys for specific providers (e.g., NanoBanana) to manage costs and access specialized models.
-   **Style Transfer & Consistency:**
    -   **Style Profiles:** Extracted from MangaDex links, these profiles include parameters like color palette, line weight, and screentone density.
    -   **Character Consistency:** Uses techniques like LoRAs (Low-Rank Adaptation) and IP-Adapter to maintain character visual consistency across different panels.

## 3. Composition Engine (Canvas-Based Editor)

The Composition Engine allows for interactive layout and arrangement of manga panels and speech bubbles.

### Client-Side Editor
-   **Framework:** Built using a canvas library like **Fabric.js** or **Konva.js**.
-   **Panel Management:** Support for dragging, resizing, and layering panels, including diagonal and overlapping layouts.
-   **Speech Bubbles:** Dynamic speech bubbles with customizable shapes, tails, and manga-style fonts.
-   **Real-time Preview:** Users can preview the final composition in real-time.

### Server-Side Rendering (SSR)
-   **Pillow (PIL):** Used on the backend for high-resolution rendering and export of the final composition, ensuring consistency with the client-side preview.
-   **Manga-Style Effects:** Post-processing layers for screentones, speed lines, and manga textures are applied during the rendering process.

## 4. Export Pipeline

The export pipeline is a separate worker task responsible for packaging the final manga into various professional formats.

-   **CBZ (Comic Book Archive):** A collection of high-resolution PNG/JPEG files in a ZIP archive.
-   **PDF:** A multi-page PDF document containing the rendered manga pages.
-   **Fixed-Layout EPUB:** A specialized EPUB format designed for professional digital e-readers, ensuring a consistent visual experience.
