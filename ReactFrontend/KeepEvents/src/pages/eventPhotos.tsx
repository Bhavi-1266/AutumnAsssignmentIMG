import { LoadEventPhotos } from "../services/LoadEvetntPhotos.ts";
import { useEffect, useState } from "react";
import type { Photo } from "../types/photos.ts";
import PhotoCard from "../components/PhotoCard.tsx";
import { useNavigate, useParams } from "react-router-dom";
import HighlightPhoto from "../components/HighlightPhoto.tsx";

function EventPhotos() {
  const navigate = useNavigate();
  const { eventId } = useParams<{ eventId: string }>();

  const [photos, setPhotos] = useState<Photo[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      setError("Not authenticated");
      return;
    }

    if (!eventId) {
      setError("Invalid event");
      return;
    }

    LoadEventPhotos(token, Number(eventId))
      .then((data) => {
        setPhotos(data.results);
      })
      .catch((err: Error) => {
        console.error("Error loading photos:", err);
        setError(err.message);
      });
  }, [eventId]);

  return (
    <div>
      <h1 className="text-xl font-bold text-center p-4">
        Event Photos
      </h1>

      {error && (
        <p className="text-red-500 text-center mb-4">
          {error}
        </p>
      )}

      {photos.length === 0 && !error ? (
        <p className="text-center text-gray-500">
          No photos found
        </p>
      ) : (
        <div
          className="
            grid
            grid-cols-1
            sm:grid-cols-2
            lg:grid-cols-3
            xl:grid-cols-4
            gap-6
            p-6
            max-w-7xl
            mx-auto
          "
        >
          {photos.map((photo) => (
            <PhotoCard
              key={photo.photoId ?? undefined}
              photo={photo}
              onClick={() => setSelectedPhoto(photo)}
            />
          ))}
        </div>
      )}

      {/* Highlight Modal */}
      {selectedPhoto && (
        <HighlightPhoto
          photo={selectedPhoto}
          onClick={() => setSelectedPhoto(null)}
        />
      )}
    </div>
  );
}

export default EventPhotos;
