import type { Photo } from "../types/photos";

interface PhotoHighlightProps {
  photo: Photo;
  onClick?: () => void;
}

function HighlightPhoto({ photo, onClick }: PhotoHighlightProps) {
  return (
    <div  onClick={onClick} className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      {/* Close */}
      <button
        type="button"
        onClick={onClick}
        className="absolute top-5 right-5 text-white text-3xl font-bold hover:text-gray-300"
      >
        ×
      </button>

      {/* Container */}
      <div  onClick={(e) => {e.stopPropagation()}}  className="max-w-6xl  z-54 w-full mx-6 bg-black rounded-lg shadow-xl flex flex-col md:flex-row overflow-hidden">
        
        {/* Image */}
        <div className="flex-1 flex items-center justify-center bg-black">
          {photo.photoFile ? (
            <img
              src={photo.photoFile}
              alt={photo.photoDesc ?? "Photo"}
              className="max-h-[85vh] w-auto object-contain"
            />
          ) : (
            <span className="text-gray-400">No Image</span>
          )}
        </div>

        {/* Details */}
        <div className="w-full md:w-96 bg-white p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold mb-2">Photo Details</h2>

          {photo.photoDesc && (
            <p className="text-sm text-gray-700 mb-3">
              {photo.photoDesc}
            </p>
          )}

          <div className="space-y-2 text-sm text-gray-600">
            <div>
              <strong>Uploaded:</strong>{" "}
              {photo.uploadDate
                ? new Date(photo.uploadDate).toLocaleString()
                : "—"}
            </div>

            <div><strong>Likes:</strong> {photo.likecount ?? 0}</div>
            <div><strong>Views:</strong> {photo.viewcount ?? 0}</div>
            <div><strong>Downloads:</strong> {photo.downloadcount ?? 0}</div>
            <div><strong>Comments:</strong> {photo.commentcount ?? 0}</div>

            {photo.extractedTags?.length && (
              <div>
                <strong>Tags:</strong>
                <div className="flex flex-wrap gap-2 mt-1">
                  {photo.extractedTags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 bg-gray-200 rounded text-xs"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {photo.event && (
              <div>
                <strong>Event:</strong> {photo.event.eventname}
              </div>
            )}

            {photo.uploadedBy && (
              <div>
                <strong>Uploaded by:</strong> {photo.uploadedBy.username}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default HighlightPhoto;
