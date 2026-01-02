export interface User {
  userid: number;
  username: string;
  email: string;
  enrollmentNo: number | null;
  dept: string | null;
  batch: number | null;
  userProfile: string | null;
  userbio: string | null;

  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;

  last_login: string | null;
  date_joined: string;

  groups: number[];
  user_permissions: number[];
}

export type EditedData = Partial<{
  userbio: string | null;
  enrollmentNo: number | null;
  dept: string | null;
  batch: number | null;
}>;



export interface UserActivitySummary {
  user: {
    username: string;
    email: string;
  };
  stats: {
    total_photos: number;
    total_likes: number;
    total_views: number;
    total_downloads: number;
    total_comments: number;
    first_upload_date: string | null;
  };
  activity: {
    top_tags: { tag: string; count: number }[];
    top_locations: { location: string; count: number }[];
    major_events: {
      event__eventid: number;
      event__eventname: string;
      photo_count: number;
    }[];
  };
}
