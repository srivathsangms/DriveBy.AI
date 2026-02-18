import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface User {
    email: string;
    role: 'driver' | 'family';
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

    useEffect(() => {
        if (token) {
            // Decode JWT to get user info (simplified) or fetch from API
            // Here we just decode base64 payload for demo
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ email: payload.sub, role: payload.role });
                localStorage.setItem('token', token);
                axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            } catch (e) {
                logout();
            }
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    const login = (newToken: string) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within an AuthProvider');
    return context;
};
