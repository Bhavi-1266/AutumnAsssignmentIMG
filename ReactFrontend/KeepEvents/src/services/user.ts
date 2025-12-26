import type { EditedData } from "../types/user";

export async function patchUserData(
  userid: number,
  data: EditedData
) {
  const response = await fetch(`/api/users/${userid}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to update user data");
  }

  return response.json();
}

export async function patchUserProfileImage(
  userid: number,
  file: File
) {
  const formData = new FormData();
  formData.append("userProfile", file);

  const response = await fetch(`/api/users/${userid}/`, {
    method: "PATCH",
    body: formData,
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to update profile image");
  }

  return response.json();
}

