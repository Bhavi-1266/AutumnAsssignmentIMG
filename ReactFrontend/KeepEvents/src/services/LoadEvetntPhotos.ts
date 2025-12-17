const API_BASE = "http://127.0.0.1:8000/api";

import type { PaginatedResponse } from "../types/pagination";
import type { Photo} from "../types/photos"  ;

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
