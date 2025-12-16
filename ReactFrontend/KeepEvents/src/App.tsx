import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/StartingPage";
import Login from "./pages/login";
import Register from "./pages/register";
import PublicPage from "./pages/public";
import { BrowserRouter } from "react-router-dom";


function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/public" element={<PublicPage />} />
      </Routes>
    </>
  );
}

export default App;
