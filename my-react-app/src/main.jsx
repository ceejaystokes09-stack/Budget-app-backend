import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/login.jsx';
import Index from './pages/Index.jsx';
// import account when created ; 

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      {/* Pages */}
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/login" element={<Login />} />
        {/* <Route path="/practice" element={<Practice />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);