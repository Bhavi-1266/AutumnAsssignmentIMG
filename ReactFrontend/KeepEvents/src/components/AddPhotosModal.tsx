import { useState } from "react";
import type { PhotoDraft } from "../types/photos";
import addMany from "../services/Photos";
import { tagImageWithBlip } from "../services/Tagging";

interface Props {   
  eventId: number;
  onClose: () => void;
  sucessCallback?: () => void;
  failureCallback?: () => void;
}

interface PhotoDraftUI extends PhotoDraft {
  file: File;
  isTagging: boolean;
}

function AddPhotosModal({ eventId, onClose , sucessCallback, failureCallback }: Props) {
  const [photos, setPhotos] = useState<PhotoDraftUI[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (!e.target.files) return;

    const files = Array.from(e.target.files);

    const drafts: PhotoDraftUI[] = files.map(file => ({
      file,
      photoDesc: "",
      extractedTags: [],
      isTagging: true,
    }));

    setPhotos(prev => [...prev, ...drafts]);

    files.forEach(async (file, idx) => {
      try {
        const tags = await tagImageWithBlip(file);

        setPhotos(prev =>
          prev.map((p, i) =>
            i === prev.length - files.length + idx
              ? { ...p, extractedTags: tags, isTagging: false }
              : p
          )
        );
      } catch {
        setPhotos(prev =>
          prev.map((p, i) =>
            i === prev.length - files.length + idx
              ? { ...p, isTagging: false }
              : p
          )
        );
      }
    });
  };

  const updatePhoto = (index: number, updates: Partial<PhotoDraftUI>) => {
    setPhotos(prev =>
      prev.map((p, i) => (i === index ? { ...p, ...updates } : p))
    );
  };

  const uploadAll = async () => {
    try {
      setIsUploading(true);

      // Strip UI-only field before sending
      const payload = photos.map(({ isTagging, ...rest }) => rest);

      await addMany(payload, eventId);
      onClose();
      sucessCallback?.();
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl p-6 overflow-y-auto max-h-[90vh]">

        <h2 className="text-xl font-bold mb-4">
          Ohh wanna Add Pictures
        </h2>

        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="bg-blue-200 p-2 rounded-md cursor-pointer hover:bg-blue-300"
        />

        {photos.map((photo, index) => (
          <div key={index} className="flex gap-4 mb-4 border p-3 rounded">
            <img
              src={URL.createObjectURL(photo.file)}
              className="w-32 h-32 object-cover rounded"
            />

            <div className="flex-1">
              <input
                type="text"
                placeholder="Description"
                className="border p-2 w-full mb-2"
                value={photo.photoDesc}
                onChange={(e) =>
                  updatePhoto(index, { photoDesc: e.target.value })
                }
              />

              <input
                type="text"
                placeholder="Tags (comma separated)"
                className="border p-2 w-full"
                value={photo.extractedTags.join(",")}
                onChange={(e) =>
                  updatePhoto(index, {
                    extractedTags: e.target.value
                      .split(",")
                      .map(t => t.trim())
                      .filter(Boolean),
                  })
                }
              />

              {photo.isTagging && (
                <p className="text-sm text-gray-500 mt-1">
                  🔍 Auto-tagging image…
                </p>
              )}

              <button
                className="bg-red-500 px-2 py-1 rounded text-white mt-2"
                onClick={() =>
                  setPhotos(prev =>
                    prev.filter((_, i) => i !== index)
                  )
                }
              >
                Remove
              </button>
            </div>
          </div>
        ))}

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="px-4 py-2 border rounded">
            Cancel
          </button>

          <button
            onClick={uploadAll}
            disabled={isUploading}
            className={`px-4 py-2 rounded text-white ${
              isUploading
                ? "bg-blue-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {isUploading ? "Uploading…" : "Upload All"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AddPhotosModal;
