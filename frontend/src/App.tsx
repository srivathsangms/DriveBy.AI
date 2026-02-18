import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { FamilyMonitor } from './pages/FamilyMonitor';

const PrivateRoute: React.FC<{ children: React.ReactNode, roles?: string[] }> = ({ children, roles }) => {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" />;
    if (roles && !roles.includes(user.role)) return <Navigate to="/" />; // Redirect if unauthorized role
    return <>{children}</>;
};

function AppRoutes() {
    const { user } = useAuth();

    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
                <PrivateRoute>
                    {user?.role === 'family' ? <Navigate to="/family" /> : <Dashboard />}
                </PrivateRoute>
            } />
            <Route path="/family" element={
                <PrivateRoute roles={['family']}>
                    <FamilyMonitor />
                </PrivateRoute>
            } />
        </Routes>
    );
}

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <AppRoutes />
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
