const API_BASE = "http://127.0.0.1:8000/api";

import type { PaginatedResponse } from "../types/pagination";
import type { Event } from "../types/event";

export type EventsResponse = PaginatedResponse<Event>;



export async function LoadEvents(Token: string) : Promise<EventsResponse> {

  
  const response = await fetch(`${API_BASE}/events/`, {
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
