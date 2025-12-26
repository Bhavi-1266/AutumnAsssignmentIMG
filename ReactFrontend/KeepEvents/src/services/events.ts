
import type { PaginatedResponse } from "../types/pagination";
import type { Photo} from "../types/photos"  ;
import type {Event} from "../types/event"
export type PhotoRespond = PaginatedResponse<Photo>;



export async function LoadEventPhotos( eventId: number) : Promise<PhotoRespond> {
  const response = await fetch(`/api/photos/?event=${eventId}`, {
    method: "GET",
    credentials: "include",
    
  });
  
  if (!response.ok) {
    throw new Error("Invalid userEmail or password");
  }
  return response.json();
  
}



type CreateEventForm = Pick<
  Event,
  | "eventname"
  | "eventdesc"
  | "eventdate"
  | "eventtime"
  | "eventlocation"
  | "visibility"
>;

export async function CreateEventApi(event: CreateEventForm) : Promise<Event> {

  
  const response = await fetch(`/api/events/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(event),
    
  });

  if (!response.ok) {
    throw new Error("Invalid user , cannot create events");
  }
  console.log(response);
  return response.json();
  
} 