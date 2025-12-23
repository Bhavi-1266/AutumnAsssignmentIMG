import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/StartingPage";
import Login from "./pages/login";
import Register from "./pages/register";
import HomePage from "./pages/homePage";
import { BrowserRouter } from "react-router-dom";
import EventPhotos from "./pages/eventPhotos";
import CreateEvent from "./pages/createEvent";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <>
    <Toaster position="top-right" />
      <Routes>
        
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/HomePage" element={<HomePage />} />
        <Route path="/events/:eventId" element={<EventPhotos />} />
        <Route path="createEvent" element={< CreateEvent/>} />
      </Routes>
    </>
  );
}   

export default App;
