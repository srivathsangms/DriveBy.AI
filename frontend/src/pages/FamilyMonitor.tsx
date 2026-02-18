import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { UserCheck } from 'lucide-react';
import axios from 'axios';

import { API_URL, WS_URL } from '../config';

interface LogData {
    fatigue_score: number;
    emotion: string;
    drowsy_status: boolean;
    driver_id?: string;
}

export const FamilyMonitor: React.FC = () => {
    const { logout } = useAuth();
    const [liveData, setLiveData] = useState<LogData | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Fetch history
        axios.get(`${API_URL}/logs/history`).then(res => {
            setHistory(res.data.slice(-50));
        });

        ws.current = new WebSocket(WS_URL);
        ws.current.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                setLiveData(message);
                setHistory(prev => [...prev.slice(-49), { timestamp: new Date().toLocaleTimeString(), ...message }]);
            } catch (e) { console.error("WS Parse Error", e); }
        };
        return () => { ws.current?.close(); };
    }, []);

    const isAlert = (liveData?.fatigue_score ?? 0) > 80;

    return (
        <div className="min-h-screen bg-gray-900 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                <header className="flex justify-between items-center bg-gray-800 p-4 rounded-lg shadow border-l-4 border-purple-500">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Family Safety Monitor</h1>
                        <p className="text-gray-400">Tracking: Active Driver</p>
                    </div>
                    <button onClick={logout} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white">Logout</button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                            <UserCheck className="mr-2 text-green-400" /> Current Status
                        </h3>
                        {liveData ? (
                            <div className="space-y-4">
                                <div className="flex justify-between items-center p-4 bg-gray-700 rounded">
                                    <span className="text-gray-300">Fatigue Score</span>
                                    <span className={`text-2xl font-bold ${isAlert ? 'text-red-500' : 'text-green-400'}`}>
                                        {liveData.fatigue_score.toFixed(1)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center p-4 bg-gray-700 rounded">
                                    <span className="text-gray-300">Emotion</span>
                                    <span className="text-xl text-blue-300 capitalize">{liveData.emotion}</span>
                                </div>
                                <div className="flex justify-between items-center p-4 bg-gray-700 rounded">
                                    <span className="text-gray-300">Alert Status</span>
                                    <span className={`font-bold ${isAlert ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
                                        {isAlert ? 'CRITICAL' : 'NORMAL'}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 py-10">Waiting for live data...</div>
                        )}
                    </div>

                    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                        <h3 className="text-xl font-bold text-white mb-4">Location & History</h3>
                        <div className="bg-gray-900 rounded-lg p-4 h-64">
                            <h4 className="text-gray-400 mb-2 text-sm">Fatigue History (Last 50 Updates)</h4>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={history}>
                                    <XAxis dataKey="timestamp" hide />
                                    <YAxis domain={[0, 100]} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
                                    <Line type="monotone" dataKey="fatigue_score" stroke="#8884d8" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
