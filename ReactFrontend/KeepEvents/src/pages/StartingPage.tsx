import { useNavigate } from "react-router-dom";
import EntryBox from "../components/EntryBox";
import "../styles/loginPage.css";

function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <h1>Welcome to KeepEvents</h1>

      <div className="flex flex-row gap-4 mt-4">
        <EntryBox
          displayText="Login"
          onClick={() => navigate("/login")}
        />

        <EntryBox
          displayText="Register"
          onClick={() => navigate("/register")}
        />

        <EntryBox
          displayText="Public"
          onClick={() => navigate("/public")}
        />
      </div>
    </div>
  );
}

export default LoginPage;
