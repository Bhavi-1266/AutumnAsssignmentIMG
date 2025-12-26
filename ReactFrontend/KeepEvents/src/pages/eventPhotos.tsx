import { LoadEventPhotos } from "../services/events.ts";
import { useEffect, useState } from "react";
import type { Photo } from "../types/photos.ts";
import PhotoCard from "../components/PhotoCard.tsx";
import { useNavigate, useParams } from "react-router-dom";
import HighlightPhoto from "../components/HighlightPhoto.tsx";
import CreateCard from "../components/CreateCard.tsx";
import AddPhotosModal from "../components/AddPhotosModal.tsx";
import type { User } from "../types/user";
import {getMe} from "../services/auth.ts"
import NavBar from "../components/navBar.tsx";
function EventPhotos() {
  const navigate = useNavigate();
  const { eventId } = useParams<{ eventId: string }>();

  const [photos, setPhotos] = useState<Photo[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);


  const [showAddPhotos, setShowAddPhotos] = useState(false);

  const [error, setError] = useState<string | null>(null);
  
  const [currentUser, setCurrentUser] = useState<User | null>(null); // currentUser
  const [loading , setLoading] = useState(true);
  useEffect(() => {
  if (!eventId) {
    setError("Invalid event");
    return;
  }

  const load = async () => {
    try {
      const data = await LoadEventPhotos(Number(eventId));

      // Defensive check
      if (!data || !Array.isArray(data.results)) {
        throw new Error("Invalid response format");
      }

      setPhotos(data.results);
      setError(null);
    } catch (err: any) {
      console.error("Error loading photos:", err);

      // User-friendly error message
      if (err.message.includes("<!doctype")) {
        setError("Authentication error. Please log in again.");
      } else {
        setError(err.message || "Failed to load photos");
      }
    }
  };

  load();
}, [eventId, showAddPhotos]);

  useEffect(() => {
      const checkAuth = async () => {
        try {
          const data = await getMe();
          setCurrentUser(data.user);
        } catch {
          setCurrentUser(null);
          navigate("/");
        } finally {
          setLoading(false);
          
        }
      };
  
      checkAuth();
    }, []);
  
    if (loading) {
      return <p>Loading...</p>;
    }
  
    if (!currentUser) {
      return <p>Not logged in</p>;
    }
  
  return (
    <div>
      <NavBar />
      <h1 className="text-xl font-bold text-center p-4">
        Event Photos
      </h1>

      {error && (
        <p className="text-red-500 text-center mb-4">
          {error}
        </p>
      )}

      {photos.length === 0 && !error ? (
         <CreateCard ToCreate="Photo" onClick={() => setShowAddPhotos(true)} />
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
          <CreateCard ToCreate="Photo" onClick={() => setShowAddPhotos(true)} />
          {photos.map((photo) => (
            <PhotoCard
              key={photo.photoId}
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

      {showAddPhotos && eventId && (
        <AddPhotosModal
          eventId={Number(eventId)}
          onClose={() =>{ 
            setShowAddPhotos(false)

          }
          }
        />
      )}

    </div>
  );
}

export default EventPhotos;
