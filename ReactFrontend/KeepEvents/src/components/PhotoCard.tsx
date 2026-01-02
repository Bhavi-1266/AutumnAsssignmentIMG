import { useState } from "react";
import type { Photo } from "../types/photos";
import { togglePhotoLike } from "../services/Photos";

interface PhotoCardProps {
  photo: Photo;
  selected : boolean
  selectionMode : boolean
  onToggleSelect?: (photoId: number) => void;
  onClick?: () => void;
}

function PhotoCard({ photo, selected,selectionMode, onToggleSelect, onClick }: PhotoCardProps) {
  const [liked, setLiked] = useState(photo.isLikedByCurrentUser);
  const [likes, setLikes] = useState(photo.likes);
  const [loading, setLoading] = useState(false);

  const handleLike = async () => {
    if (loading) return;

    // optimistic UI update
    setLiked(!liked);
    setLikes((prev) => (liked ? prev - 1 : prev + 1));
    setLoading(true);

    try {
      const res = await togglePhotoLike(photo.photoid);
      setLiked(res.liked);
      setLikes(res.likes);
    } catch (err) {
      // rollback on failure
      setLiked(liked);
      setLikes(likes);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`flex flex-col rounded-lg h-full border border-gray-300 shadow-md hover:shadow-lg cursor-pointer transition-shadow duration-200 bg-white"
        ${selected ? "ring-2 ring-blue-500" : "hover:shadow-lg"}`}
      onClick={() => {
        if (selectionMode) {
          onToggleSelect?.(photo.photoid);
        } else {
          onClick?.();
        }
      }}>

      {/* Selection checkbox */}
      <div
        className="relative top-2 left-2 z-10"
        onClick={(e) => {
          e.stopPropagation(); // 🔴 critical
          onToggleSelect?.(photo.photoid);
        }}
      >
        <div
          className={`w-5 h-5 rounded border flex items-center justify-center
            ${selected
              ? "bg-blue-600 border-blue-600"
              : "bg-black/20 border-white"
            }`}
        >
          {selected && <span className="text-white text-xs">✓</span>}
        </div>
      </div>
      {/* Image */}
      <div className="relative">
        {photo.photoFile ? (
          <img
            src={photo.photoFile}
            alt={photo.photoDesc || "Photo"}
            className="h-48 w-full object-contain select-none pointer-events-auto"
            onContextMenu={(e) => e.preventDefault()}
            draggable={false}
          />
        ) : (
          <div className="h-48 w-full flex items-center justify-center text-gray-500">
            No Image
          </div>
        )}
      </div>

      {/* Footer */}
      <div
        className="flex items-center px-3 py-2 border-t border-gray-200"
        onClick={(e) => e.stopPropagation()} // prevent opening photo
      >
        <button
          onClick={handleLike}
          disabled={loading}
          className="flex items-center gap-1"
          aria-label="Like photo"
        >
          {/* Heart SVG */}
          <svg
            viewBox="0 0 24 24"
            className={`w-6 h-6 transition ${
              liked
                ? "fill-red-500 stroke-red-500"
                : "fill-white stroke-red-500"
            }`}
            strokeWidth={2}
          >
            <path d="M12 21s-6.7-4.35-9.33-7.28C.94 11.74 1.6 7.99 4.9 6.5c2.06-.93 4.29-.14 5.6 1.38C11.81 6.36 14.04 5.57 16.1 6.5c3.3 1.49 3.96 5.24 2.23 7.22C18.7 16.65 12 21 12 21z" />
          </svg>

          <span className="text-sm text-gray-700">
            {likes}
          </span>
        </button>
      </div>
    </div>
  );
}

export default PhotoCard;


