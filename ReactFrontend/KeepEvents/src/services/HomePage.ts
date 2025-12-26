import type { PaginatedResponse } from "../types/pagination";
import type { Event } from "../types/event";
export type EventsResponse = PaginatedResponse<Event>;

export async function LoadEvents() : Promise<EventsResponse> {

  
  const response = await fetch(`/api/events/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    
  });

  if (!response.ok) {
    throw new Error("Invalid userEmail or password");
  }
  console.log(response);
  return response.json();
  
}
