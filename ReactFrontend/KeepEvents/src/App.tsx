import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/StartingPage";
import Login from "./pages/login";
import Register from "./pages/register";
import PublicPage from "./pages/public";
import HomePage from "./pages/homePage";
import { BrowserRouter } from "react-router-dom";
import EventPhotos from "./pages/eventPhotos";


function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/public" element={<PublicPage />} />
        <Route path="/HomePage" element={<HomePage />} />
        <Route path="/events/:eventId" element={<EventPhotos />} />
      </Routes>
    </>
  );
}

export default App;
