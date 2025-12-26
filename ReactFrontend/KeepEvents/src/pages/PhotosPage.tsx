import NavBar from "../components/navBar";
import { use, useEffect, useState } from "react";
import {getMe} from "../services/auth";
function PhotosPage() {
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
            <h1>PhotosPage</h1>
        </div>
    );
}

export default PhotosPage;