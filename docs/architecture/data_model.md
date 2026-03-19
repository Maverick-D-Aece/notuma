# Data Model

NoTuMa uses a relational database (PostgreSQL) and S3-compatible object storage to manage its persistent data. The following documentation outlines the data schema and storage strategy.

## Entity Relationship Diagram (ERD)

The relational schema is centered around users, projects, chapters, and the visual assets that make up a manga.

```prisma
// Using Prisma schema syntax as a representation

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String    @id @default(uuid())
  email     String    @unique
  name      String?
  projects  Project[]
  apiKey    String?   // For BYOK features
  createdAt DateTime  @default(now())
}

model Project {
  id          String      @id @default(uuid())
  title       String
  description String?
  userId      String
  user        User        @relation(fields: [userId], references: [id])
  chapters    Chapter[]
  characters  Character[]
  styleId     String?
  style       StyleProfile? @relation(fields: [styleId], references: [id])
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
}

model Chapter {
  id        String   @id @default(uuid())
  title     String
  order     Int
  projectId String
  project   Project  @relation(fields: [projectId], references: [id])
  scenes    Scene[]
  pages     Page[]
  content   String   // Raw text of the chapter
  createdAt DateTime @default(now())
}

model Scene {
  id          String      @id @default(uuid())
  order       Int
  chapterId   String
  chapter     Chapter     @relation(fields: [chapterId], references: [id])
  text        String
  description String?     // Generated prompt description
  dialogues   Dialogue[]
  panels      Panel[]
  createdAt   DateTime    @default(now())
}

model Character {
  id           String   @id @default(uuid())
  name         String
  description  String?
  traits       String[] // Physical traits (hair color, eye color, etc.)
  projectId    String
  project      Project  @relation(fields: [projectId], references: [id])
  visualRefUrl String?  // Link to a reference image in S3
  loraId       String?  // Associated LoRA ID for consistency
  createdAt    DateTime @default(now())
}

model Dialogue {
  id          String    @id @default(uuid())
  characterId String?
  character   Character? @relation(fields: [characterId], references: [id])
  sceneId     String
  scene       Scene      @relation(fields: [sceneId], references: [id])
  text        String
  order       Int
}

model Page {
  id        String   @id @default(uuid())
  order     Int
  chapterId String
  chapter   Chapter  @relation(fields: [chapterId], references: [id])
  layout    Json     // Canvas layout data (panel positions, bubbles)
  imageUrl  String?  // Rendered page image URL in S3
  createdAt DateTime @default(now())
}

model Panel {
  id       String @id @default(uuid())
  sceneId  String
  scene    Scene  @relation(fields: [sceneId], references: [id])
  imageUrl String // Generated image URL in S3
  prompt   String
  style    Json?  // Style parameters used
}

model StyleProfile {
  id              String   @id @default(uuid())
  name            String
  sourceUrl       String?  // MangaDex or reference link
  features        Json     // Extracted style features (color, line weight)
  projects        Project[]
}
```

## Storage Strategy

Assets are stored in S3-compatible object storage (Cloudflare R2 or AWS S3) with the following directory structure:

```
/notuma-assets
  /uploads
    /{projectId}/{chapterId}/raw_novel.txt
  /characters
    /{projectId}/{characterId}/{characterId}_ref.png
  /generated
    /{projectId}/{chapterId}/{sceneId}/panel_{panelId}.png
  /exports
    /{projectId}/{chapterId}/chapter_{chapterId}.pdf
    /{projectId}/{chapterId}/chapter_{chapterId}.cbz
    /{projectId}/{chapterId}/chapter_{chapterId}.epub
```

-   **Public Access:** Generated images and exports are served via a CDN or a signed URL for temporary access.
-   **Versioning:** S3 versioning may be enabled for critical assets like raw novel uploads.
