
import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, Activity, Smile, Eye } from 'lucide-react';
import axios from 'axios';
import { API_URL, WS_URL } from '../config';

interface LogData {
    fatigue_score: number;
    emotion: string;
    drowsy_status: boolean;
    ear?: number;
    mar?: number;
}

export const Dashboard: React.FC = () => {
    const { user, logout } = useAuth();
    const [data, setData] = useState<LogData | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Fetch initial history
        axios.get(`${API_URL}/logs/history`).then(res => {
            setHistory(res.data.slice(-20)); // Limit for chart
        });

        // Connect WebSocket
        ws.current = new WebSocket(WS_URL);

        ws.current.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                // If the message is from the driver (AI Engine), it might be raw or formatted.
                // Assuming simple structure match
                setData(message);
                setHistory(prev => [...prev.slice(-19), { timestamp: new Date().toLocaleTimeString(), ...message }]);
            } catch (e) { console.error("WS Parse Error", e); }
        };

        return () => {
            ws.current?.close();
        };
    }, []);

    if (!user) return null;

    const isDrowsy = (data?.fatigue_score ?? 0) > 80;

    return (
        <div className={`min-h-screen p-6 transition-colors duration-500 ${isDrowsy ? 'bg-red-900/20' : 'bg-gray-900'}`}>
            <div className="max-w-7xl mx-auto space-y-6">
                <header className="flex justify-between items-center bg-gray-800 p-4 rounded-lg shadow">
                    <div>
                        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">DriveBy.AI Dashboard</h1>
                        <p className="text-gray-400">Driver: {user.email}</p>
                    </div>
                    <button onClick={logout} className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded">Logout</button>
                </header>

                {isDrowsy && (
                    <div className="animate-pulse bg-red-600 text-white p-4 rounded-lg flex items-center justify-center text-3xl font-bold shadow-lg border-4 border-red-800">
                        <AlertTriangle className="w-10 h-10 mr-4" />
                        DROWSINESS ALERT! PULL OVER!
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-gray-800 p-6 rounded-lg shadow border border-gray-700">
                        <h3 className="text-gray-400 flex items-center mb-2"><Activity className="w-4 h-4 mr-2" /> Fatigue Score</h3>
                        <div className={`text-5xl font-bold ${isDrowsy ? 'text-red-500' : 'text-green-400'}`}>
                            {data?.fatigue_score?.toFixed(1) || 0}
                        </div>
                        <div className="text-sm text-gray-500 mt-2">Threshold: 80</div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg shadow border border-gray-700">
                        <h3 className="text-gray-400 flex items-center mb-2"><Smile className="w-4 h-4 mr-2" /> Emotion</h3>
                        <div className="text-4xl font-bold text-blue-400 capitalize">
                            {data?.emotion || 'Neutral'}
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg shadow border border-gray-700">
                        <h3 className="text-gray-400 flex items-center mb-2"><Eye className="w-4 h-4 mr-2" /> Eye Status</h3>
                        <div className={`text-4xl font-bold ${data?.drowsy_status ? 'text-red-400' : 'text-green-400'}`}>
                            {data?.drowsy_status ? 'CLOSED' : 'OPEN'}
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 p-6 rounded-lg shadow border border-gray-700 h-96">
                    <h3 className="text-gray-400 mb-4">Fatigue Trend</h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={history}>
                            <XAxis dataKey="timestamp" hide />
                            <YAxis domain={[0, 100]} />
                            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
                            <Line type="monotone" dataKey="fatigue_score" stroke="#8884d8" strokeWidth={3} dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
