import { NavLink, useNavigate } from "react-router-dom";
import LogoutButton from "./Logout";

function NavBar() {
  const navigate = useNavigate();

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? "text-yellow-300 border-b-2 border-yellow-300 pb-1"
      : "text-white hover:text-blue-200 transition";

  return (
    <header className="w-full">
      {/* Top Branding Bar */}
      <div className="bg-blue-900 text-white text-sm px-6 py-1">
        Keep Events
      </div>

      {/* Main Navbar */}
      <nav className="flex items-center justify-between h-16 bg-blue-600 px-6 shadow-md">
        {/* Left: Website Name */}
        <div
          className="text-white font-semibold text-lg cursor-pointer"
          onClick={() => navigate("/HomePage")}
        >
          KeepEvents
        </div>

        {/* Center: Navigation Links */}
        <ul className="flex space-x-6 font-medium">
          <li>
            <NavLink to="/HomePage" className={navLinkClass}>
              Home
            </NavLink>
          </li>

          <li>
            <NavLink to="/Events" className={navLinkClass}>
              Events
            </NavLink>
          </li>

          <li>
            <NavLink to="/Photos" className={navLinkClass}>
              Photos
            </NavLink>
          </li>

          <li>
            <NavLink to="/Profile" className={navLinkClass}>
              My Info
            </NavLink>
          </li>
        </ul>

        {/* Right: Actions */}
        <div className="flex items-center space-x-3">
          <NavLink
            to="/Activity"
            className={({ isActive }) =>
              isActive
                ? "bg-yellow-400 text-blue-900 px-4 py-1.5 rounded font-medium"
                : "bg-blue-500 hover:bg-blue-400 text-white px-4 py-1.5 rounded transition"
            }
          >
            My Activity
          </NavLink>

          <LogoutButton onLoggedOut={() => navigate("/login")} />

          
        </div>
      </nav>
    </header>
  );
}

export default NavBar;
