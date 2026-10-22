import { createContext, useContext, useState } from 'react';
import api from '../api/client'

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem('token'));

    async function login(email, password) {
        const body = {
            email: email,
            password: password
        }
        const response = await api.post('/login', body)
        localStorage.setItem('token', response.data.access_token)
        setToken(response.data.access_token)
    }

    function logout() {
        localStorage.removeItem('token')
        setToken(null)
    }
    const value = {token, login, logout};

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
} 

export function useAuth() {
    return useContext(AuthContext)
}