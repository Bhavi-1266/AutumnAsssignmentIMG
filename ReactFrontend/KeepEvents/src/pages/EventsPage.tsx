import NavBar from "../components/navBar";
import { useEffect , useState} from "react";
import {getMe} from "../services/auth";
function EventsPage() {
    useEffect(() => {
            const checkAuth = async () => {
                try {
                    const data = await getMe();
                } catch {
                    window.location.href = "/login";
                }
            };
            checkAuth();
        }, []);
    return (
        <div>
            <NavBar />
            <h1>EventsPage</h1>
        </div>
    );
}

export default EventsPage;