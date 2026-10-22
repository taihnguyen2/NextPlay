import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function Signup() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    async function handleSubmit(e) {
        e.preventDefault(); 
        setErrorMessage("");

        try {
            const body = {
                email: email,
                password: password
            }
            await api.post('/signup', body);
            await login(email,password);
            navigate('/recommendations');
        } catch (err) {
            setErrorMessage("Email already being used");
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <h1>Sign up</h1>
                <input
                    type="email"
                    placeholder="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                /> 
                <input
                    type="password"
                    placeholder="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
            {errorMessage && <p>{errorMessage}</p>}
            <button type="submit">Sign up</button>
            <p>
                Already have an account? <Link to ="/login">Log in</Link>
            </p>
        </form>
    );
}