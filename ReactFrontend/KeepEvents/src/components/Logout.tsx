import { logout } from "../services/auth";

function LogoutButton({ onLoggedOut }: { onLoggedOut: () => void }) {
  const handleLogout = async () => {
    try {
      await logout();
      onLoggedOut(); // clear user state
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition duration-300"
    >
      Logout
    </button>
  );
}

export default LogoutButton;
