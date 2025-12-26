import { LoadEvents } from "../services/homePage";
import { useEffect, useState } from "react";
import type { Event } from "../types/event";
import EventCard from "../components/EventCard";
import { useNavigate } from "react-router-dom";
import CreateCard from "../components/CreateCard";
import type {User}  from "../types/user";
import {getMe} from "../services/auth"
import Logout from "../components/Logout";
import NavBar from "../components/navBar";
function HomePage() {
        const navigate = useNavigate();
        const [events, setEvents] = useState<Event[]>([]);
        const [error, setError] = useState<string | null>(null);
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);



    useEffect(() => {
    const checkAuth = async () => {
      try {
        const data = await getMe();
        setCurrentUser(data.user);
      } catch {
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    const loadEvents = async () => {
      try {
        const data = await LoadEvents();
        setEvents(data.results);
      } catch (err: any) {
        setError(err.message);
      }
    };

    loadEvents();
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
      
          {error && (
            <p className="text-red-500 text-center mb-4">
              {error}
            </p>
          )}

          {events.length === 0 ? (

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
                <CreateCard ToCreate="Event" onClick={() => navigate("/EventsCreate")} />
              
                </div>
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
                <CreateCard ToCreate="Event" onClick={() => navigate("/EventsCreate")} />
                {events.map((event) => (
                    <EventCard
                    key={event.eventid}
                    event={event}
                    totalPhotos={12}
                    onClick={() => navigate(`/Events/${event.eventid}`)}
                    />
                ))}
                </div>
            )}
      </div>

    );
}

export default HomePage;
