import { createContext, useContext, useState } from 'react';
import api from '../api/client'

const AuthContext = createContext();

export function AuthProvider({ children }) {
    // 1. What piece of state tracks whether someone is logged in?
    //    (hint: you could derive this from whether a token exists,
    //    rather than tracking a separate boolean)
    const [token, setToken] = useState(localStorage.getItem('token'));

    // 2. login(email, password) — should:
    //    - POST to /login via `api`
    //    - on success, store the returned token in localStorage
    //    - on failure, let the caller (your Login page) handle showing an error
    async function login(email, password) {
        const body = {
            email: email,
            password: password
        }
        try {
            const response = await api.post('/login', body)
        } catch 
        localStorage.setItem('token', response.data.access_token)
        setToken(response.data.access_token)
    }

    // 3. logout() — should:
    //    - remove the token from localStorage
    //    - update whatever state tracks logged-in status

    const value = {
        // expose login, logout, and current auth state here
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
} 

export function useAuth() {
    return useContext(AuthContext)
}