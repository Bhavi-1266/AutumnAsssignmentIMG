const API_BASE = "http://127.0.0.1:8000/api";

import type { User } from "../types/user";

export async function getMyData(token: string): Promise<User> {
  const userId = localStorage.getItem("userId");

  if (!userId) {
    throw new Error("User ID not found in localStorage");
  }

  const response = await fetch(`${API_BASE}/users/${userId}/`, {
    method: "GET",
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Cannot fetch user info");
  }

  const data: User = await response.json();
  return data;
}
