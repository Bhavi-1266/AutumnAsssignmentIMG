import { LoadEvents } from "../services/HomePage";
import { useEffect, useState } from "react";
import type { Event } from "../types/event";
import EventCard from "../components/EventCard";
import { useNavigate } from "react-router-dom";


function HomePage() {
        const navigate = useNavigate();
        const [events, setEvents] = useState<Event[]>([]);
        const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
        setError("Not authenticated");
        return;
        }

        LoadEvents(token)
        .then((data) => {
            console.log("Events loaded:", data);
            setEvents(data.results);
        })
        .catch((err) => {
            console.error("Error loading events:", err);
            setError(err.message);
        });
    }, []);

    return (
        <div>
  <h1 className="text-xl font-bold text-center p-4">
    Home Page
  </h1>

  {error && (
    <p className="text-red-500 text-center mb-4">
      {error}
    </p>
  )}

  {events.length === 0 ? (
    <p className="text-center text-gray-500">
      No events found
    </p>
  ) : (
        <div className="
        grid
        grid-cols-1
        sm:grid-cols-2
        lg:grid-cols-3
        xl:grid-cols-4
        gap-6
        p-6
        max-w-7xl
        mx-auto
        ">
        {events.map((event) => (
            <EventCard
            key={event.eventid}
            event={event}
            totalPhotos={12}
            onClick={() => navigate(`/events/${event.eventid}`)}
            />
        ))}
        </div>
    )}
    </div>

    );
}

export default HomePage;
