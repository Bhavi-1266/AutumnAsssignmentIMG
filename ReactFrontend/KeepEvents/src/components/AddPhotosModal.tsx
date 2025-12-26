import { useState } from "react";
import type { PhotoDraft } from "../types/photos";
import addMany from "../services/addPhotos.ts";

interface Props {   
  eventId: number;
  onClose: () => void;
}

function AddPhotosModal({ eventId, onClose }: Props) {
  const [photos, setPhotos] = useState<PhotoDraft[]>([]);
  const [isUploading, setIsUploading] = useState(false);


  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    const drafts: PhotoDraft[] = Array.from(e.target.files).map(file => ({
      file,
      photoDesc: "",
      extractedTags: [],
    }));

    setPhotos(prev => [...prev, ...drafts]);
  };

  const updatePhoto = (index: number, updates: Partial<PhotoDraft>) => {
    setPhotos(prev =>
      prev.map((p, i) => (i === index ? { ...p, ...updates } : p))
    );
  };

  const uploadAll = async () => {
  try {
    setIsUploading(true);
    await addMany(photos, eventId);
    onClose();
  } finally {
    setIsUploading(false);
  }
};


  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl p-6 overflow-y-auto max-h-[90vh]">

        <h2 className="text-xl font-bold mb-4">Ohh wanna Add Pictures </h2>
            <input
            type="file"
            multiple
            accept="image/*"
            
            onChange={handleFileSelect}
            
            className="bg-blue-200 p-2 rounded-md  cursor-pointer text-center hover:bg-blue-300 transition duration-300 "
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
                      .map(t => t.trim()),
                  })
                }
              />
              <button
                className=" bg-red-500 px-2 py-1  rounded text-red-100 mt-1 hover:bg-red-600 text-sm-center "
                onClick={() => setPhotos(prev => prev.filter((_, i) => i !== index))}
              >x
              </button>
            </div>
          </div>
        ))}

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={uploadAll}
            disabled={isUploading}
            className={`
                px-4 py-2 rounded text-white flex items-center justify-center
                ${isUploading ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}
            `}
            >
            {isUploading ? (
                <span
                className="
                    w-5 h-5 border-2 border-white border-t-transparent
                    rounded-full animate-spin
                "
                />
            ) : (
                "Upload All"
            )}
            </button>
        </div>
      </div>
    </div>
  );
}

export default AddPhotosModal;
