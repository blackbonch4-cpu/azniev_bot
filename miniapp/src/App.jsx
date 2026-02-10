import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import PurchasesPage from './pages/PurchasesPage';
import SupportPage from './pages/SupportPage';
import AdminPanel from './pages/AdminPanel';
import AddWebinar from './pages/AddWebinar';
import EditWebinar from './pages/EditWebinar';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/purchases" element={<PurchasesPage />} />
            <Route path="/support" element={<SupportPage />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/admin/add" element={<AddWebinar />} />
            <Route path="/admin/edit/:id" element={<EditWebinar />} />
          </Routes>
          <Navigation />
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
