import type { User } from "./user.ts";
import type { Event } from "./event.ts";

export interface Photo {
    photoId: number | null;
    photoDesc: string | null;
    photoFile: string | null;
    uploadDate: string | null;
    extractedTags: string[] | null;
    photoMeta: string[] | null;
    likecount: number | null;
    viewcount: number | null;
    downloadcount: number | null;
    commentcount: number | null;

    event: Event | null;
    uploadedBy: User | null;
}

export interface PhotoDraft {
  file: File;
  photoDesc: string;
  extractedTags: string[];
}
