const API_BASE = "http://127.0.0.1:8000/api";

import type { PaginatedResponse } from "../types/pagination";
import type { Photo} from "../types/photos"  ;
import type {Event} from "../types/event"
export type PhotoRespond = PaginatedResponse<Photo>;



export async function LoadEventPhotos(Token: string , eventId: number) : Promise<PhotoRespond> {

  
  const response = await fetch(`${API_BASE}/photos/?event=${eventId}`, {
    method: "GET",
    headers: {
      "Authorization": `Token  ${Token}`,
      "Content-Type": "application/json",
    },
    
  });

  if (!response.ok) {
    throw new Error("Invalid userEmail or password");
  }
  console.log(response);
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

export async function CreateEventApi(Token: string , event: CreateEventForm) : Promise<Event> {

  
  const response = await fetch(`${API_BASE}/events/`, {
    method: "POST",
    headers: {
      "Authorization": `Token  ${Token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(event),
    
  });

  if (!response.ok) {
    throw new Error("Invalid user , cannot create events");
  }
  console.log(response);
  return response.json();
  
} 