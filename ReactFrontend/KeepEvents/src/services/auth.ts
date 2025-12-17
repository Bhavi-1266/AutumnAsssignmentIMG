const API_BASE = "http://127.0.0.1:8000/api";

export async function login(userEmail: string, password: string) {

  const body = {
    email: userEmail,
    password,
  }
  console.log(JSON.stringify(body));
  const response = await fetch(`${API_BASE}/users/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error("Invalid userEmail or password");
  }
  console.log(response);
  return response.json();
  
}
