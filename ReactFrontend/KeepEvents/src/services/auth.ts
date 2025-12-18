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


export async function register(userEmail: string, password: string , name: string) {

  const body = {
    email: userEmail,
    username : name,
    password,
    
  }
  console.log(JSON.stringify(body));
  const response = await fetch(`${API_BASE}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body), 
  });

  // if (!response.ok) {
  //   throw new Error("Registration failed");
   
  // }
  console.log(response);
  return response.json();
}


export async function resendOTP(userEmail: string) {
  const body = {
    email: userEmail,
  }
  const response = await fetch(`${API_BASE}/auth/request-otp/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  // if (!response.ok) {
  //   throw new Error("Failed to resend OTP");
  // }
  return response.json();

}

export async function verifyOTP(userEmail: string, otp: string) {
  const body = {
    email: userEmail,
    code : otp,
  }
  const response = await fetch(`${API_BASE}/auth/verify-otp/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  console.log(response);
  if (!response.ok) {
    throw new Error("Failed to verify OTP");
  }
  return response.json();

} 