import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    async function handleSubmit(e) {
        e.preventDefault(); 
        setErrorMessage("");
        try {
            await login(email, password);
            navigate('/recommendations');
        } catch (err) {
            setErrorMessage("Incorrect email or password");
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <h1>Log in</h1>
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
            <button type="submit">Log in</button>
            <p>
                Don't have an account? <Link to="/signup">Sign up</Link>
            </p>
        </form>
    );
}