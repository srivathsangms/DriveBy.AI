
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

export const Register: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [role, setRole] = useState('driver');
    const { login } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:8000/auth/register', {
                email,
                password,
                name,
                role
            });
            login(res.data.access_token);
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed. Try again.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-900">
            <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-xl">
                <h2 className="text-3xl font-bold text-center text-white">Join DriveBy.AI</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300">Name</label>
                        <input type="text" value={name} onChange={e => setName(e.target.value)}
                            className="w-full px-4 py-2 mt-1 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white" required />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300">Email</label>
                        <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                            className="w-full px-4 py-2 mt-1 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white" required />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300">Role</label>
                        <select value={role} onChange={e => setRole(e.target.value)}
                            className="w-full px-4 py-2 mt-1 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                            <option value="driver">Driver</option>
                            <option value="family">Family/Monitor</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300">Password</label>
                        <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                            className="w-full px-4 py-2 mt-1 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-white" required />
                    </div>
                    {error && <p className="text-red-500 text-sm">{error}</p>}
                    <button type="submit" className="w-full py-2 font-bold text-white bg-green-600 rounded hover:bg-green-700 transition">
                        Register
                    </button>
                    <div className="text-center mt-4">
                        <Link to="/login" className="text-blue-400 hover:text-blue-300 text-sm">
                            Already have an account? Login here
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};
