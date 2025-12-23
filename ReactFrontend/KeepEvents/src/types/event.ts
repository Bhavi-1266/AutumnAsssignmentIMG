import type { User } from "./user";

export type EventVisibility = "public" | "admin" | "img";

export interface Event {
  eventid: number;
  eventname: string;
  eventdesc: string | null;
  eventdate: string | null;     // YYYY-MM-DD
  eventtime: string | null;     // HH:MM:SS 
  eventlocation: string | null;

  eventCoverPhoto: string | null;
  eventCoverPhoto_url: string | null;

  eventCreator: number;
  eventCreator_detail: User;

  visibility: EventVisibility;
}
