import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register, resendOTP, verifyOTP } from "../services/auth";

function Register() {
  const navigate = useNavigate();
  const [userEmail, setuserEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [takeOTP, setTakeOTP] = useState(false);
  const [otp, setOTP] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    register(userEmail, password, name)
      .then((data) => {
        if (!data.hasOwnProperty("userid")) {
          console.log("in user id not found");
          if (data.is_active === "False") { // "as error is returning only in string , not in bool"
            console.log("in user id not found --- otp sending");
            resendOTP(userEmail)
              .then(() => {
                setTakeOTP(true);
              })
              .catch((err) => {
                console.log(err);
                setError("OTP send failed try again later.");
              });
          } else {
            console.log("in user id not found --- otp not sending");
            if (data.username) {
              setError(data.username[0]);
            } else if (data.email) {
              setError(data.email[0]);
            } else {
              setError("Registration failed try again later.");
            }
          }
        } else {
          console.log("IN userid found");

          if (data.is_active === false) { // here false not a string as working 
            console.log("IN userid found --- otp sending");
            resendOTP(userEmail)
              .then(() => {
                setTakeOTP(true);
              })
              .catch((err) => {
                console.log(err);
                setError("OTP resend failed try again later.");
              });
          } else {
            throw new Error("Registration failed try again later.");
          }
        }
      })
      .catch((err) => {
        console.log(err);
        setError("Invalid credentials");
      });
  }

  async function handleSubmitOTP(e: React.FormEvent) {
    e.preventDefault();

    verifyOTP(userEmail, otp)
      .then((data) => {
        if (data.token) {
          localStorage.setItem("token", data.token);
          navigate("/HomePage");
        } else {
          setError("Registration failed try again later.");
        }
      })
      .catch((err) => {
        console.log(err);
        setError("Invalid credentials");
      });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md px-4">
        <form
          onSubmit={takeOTP ? handleSubmitOTP : handleSubmit}
          className="bg-white p-8 rounded-xl shadow-lg border border-gray-100"
        >
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-1">
              {takeOTP ? "Verify OTP" : "Create Account"}
            </h2>
            <p className="text-sm text-gray-500">
              {takeOTP
                ? "Enter the verification code sent to your email"
                : "Sign up to get started"}
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="text"
                placeholder="your.email@example.com"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors outline-none"
                value={userEmail}
                onChange={(e) => setuserEmail(e.target.value)}
                disabled={takeOTP}
              />
            </div>

            {!takeOTP && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    placeholder="Your full name"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors outline-none"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors outline-none"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </>
            )}

            {takeOTP && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Verification Code
                </label>
                <input
                  type="text"
                  placeholder="Enter 6-digit code"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors outline-none text-center text-lg tracking-widest"
                  value={otp}
                  onChange={(e) => setOTP(e.target.value)}
                  maxLength={6}
                />
              </div>
            )}
          </div>

          <button
            type="submit"
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors shadow-sm hover:shadow-md"
          >
            {takeOTP ? "Verify & Continue" : "Create Account"}
          </button>

          {takeOTP && (
            <button
              type="button"
              onClick={() => {
                resendOTP(userEmail)
                  .then(() => {
                    setError("");
                    alert("OTP resent successfully!");
                  })
                  .catch((err) => {
                    console.log(err);
                    setError("Failed to resend OTP");
                  });
              }}
              className="w-full mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Resend Code
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

export default Register;