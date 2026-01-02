import { useEffect, useState } from "react";
import { useParams , useNavigate } from "react-router-dom";
import { acceptEventInvite } from "../services/events";
import { getMe } from "../services/auth";
import type { User } from "../types/user";
import { toast } from "react-hot-toast";


function AcceptInvite() {
  const { token } = useParams<{ token: string }>();
    const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [declined, setDeclined] = useState(false);
  const [error, setError] = useState<string | null>(null);
  

  // ----------------------------
  // Check login status
  // ----------------------------
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const me = await getMe();
        setCurrentUser(me.user);
      } catch {
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  // ----------------------------
  // Accept invite
  // ----------------------------
  const handleAccept = async () => {
    if (!token) return;

    setAccepting(true);
    try {
      await acceptEventInvite(token);
      setAccepted(true);
      toast.success("Invite accepted!");
    } catch (e: any) {
      toast.error(e.message || "Failed to accept invite");
    } finally {
      setAccepting(false);
      navigate("/HomePage"); // nav
    }
  };

  // ----------------------------
  // Decline invite (frontend only)
  // ----------------------------
  const handleDecline = () => {

    setDeclined(true);
    toast.error("Invite declined!");
    navigate("/HomePage");
  };

  // ----------------------------
  // RENDER
  // ----------------------------
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Checking invite…
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        Invalid invite link
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">


        {/* Main UI */}
        {!accepted && !declined && (
          <>
            <h2 className="text-2xl font-bold text-center mb-4">
              Event Invitation
            </h2>

            {/* Not logged in */}
            {!currentUser && (
              <div className="space-y-4">
                <p className="text-gray-600 text-center">
                  Please log in or register to accept this invite.
                </p>

                <div className="flex gap-3" 
                
                >
                  <div
                  onClick = {() => navigate("/login")}
                    className="flex-1 text-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Login
                  </div>
                  <div
                    onClick = {() => navigate("/register")}
                    className="flex-1 text-center px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Register
                  </div>
                </div>
              </div>
            )}

            {/* Logged in */}
            {currentUser && (
              <div className="space-y-6">
                <p className="text-gray-700 text-center">
                  You are logged in as{" "}
                  <span className="font-semibold">
                    {currentUser.username}
                  </span>
                </p>

                <div className="flex gap-3">
                  <button
                    onClick={handleDecline}
                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                    disabled={accepting}
                  >
                    Decline
                  </button>

                  <button
                    onClick={handleAccept}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    disabled={accepting}
                  >
                    {accepting ? "Accepting…" : "Accept Invite"}
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {error && (
          <p className="text-red-600 text-sm mt-4 text-center">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

export default AcceptInvite;
