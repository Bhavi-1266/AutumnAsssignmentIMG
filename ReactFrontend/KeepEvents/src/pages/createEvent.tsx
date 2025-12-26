import { useEffect, useState } from "react";
import type { Event } from "../types/event";
import type { User } from "../types/user";
import {  CreateEventApi } from "../services/events";
import { useNavigate } from "react-router-dom";
import toast  from "react-hot-toast";
import {getMe}  from "../services/auth";
import NavBar from "../components/navBar";
type CreateEventForm = Pick<
  Event,
  | "eventname"
  | "eventdesc"
  | "eventdate"
  | "eventtime"
  | "eventlocation"
  | "visibility"
>;

function CreateEvent() {
  const [form, setForm] = useState<CreateEventForm>({
    eventname: "",
    eventdesc: "",
    eventdate: "",
    eventtime: "",
    eventlocation: "",
    visibility: "public",
  });

  const [error , setError] = useState<string | null>(null);
  // Logged-in user (event manager / creator)

  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

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



  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(form);

    CreateEventApi(form)
      .then((data) => {
        console.log(data);
        toast.success("Event created successfully");

        navigate("/HomePage");
      })
      .catch((err) => {
        toast.error("Event creation failed");

      });
  };

  return (
    <>
    <NavBar />
    <div className="max-w-md mx-auto mt-10 p-6 bg-white shadow rounded">
      
      <h2 className="text-lg font-semibold mb-4">Create Event</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Event Manager (Read Only) */}
        <input
          value={
            currentUser
              ? `Event Creator: ${currentUser.username}`
              : "Loading user..."
          }
          disabled
          className="w-full border p-2 rounded bg-gray-100 text-gray-600 cursor-not-allowed"
        />
        {error && <h2>{error}</h2>}
        <input
          name="eventname"
          placeholder="Event Name"
          value={form.eventname}
          onChange={handleChange}
          className="w-full border p-2 rounded"
          required
        />

        <textarea
          name="eventdesc"
          placeholder="Description"
          value={form.eventdesc ?? ""}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <input
          type="date"
          name="eventdate"
          value={form.eventdate ?? ""}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <input
          type="time"
          name="eventtime"
          value={form.eventtime ?? ""}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <input
          name="eventlocation"
          placeholder="Location"
          value={form.eventlocation ?? ""}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <select
          name="visibility"
          value={form.visibility}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        >
          <option value="public">Public</option>
          <option value="img">IMG</option>
          <option value="admin">Admin</option>
        </select>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Create Event
        </button>
      </form>
    </div>
  </>
  );
}

export default CreateEvent;
