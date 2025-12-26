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
  first_name: string;
  last_name: string;
  userbio: string | null;
  enrollmentNo: number | null;
  dept: string | null;
  batch: number | null;
}>;
  