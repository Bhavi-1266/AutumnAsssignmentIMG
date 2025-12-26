import { useEffect , useState} from "react";
import {getMe} from "../services/auth";
import NavBar from "../components/navBar";
function MyActivityPage() {
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
            <h1>My Activity Page</h1>
        </div>
    );
}

export default MyActivityPage