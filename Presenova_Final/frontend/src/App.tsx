/**
 * App Component
 * Main routing configuration using react-router-dom
 * All routes are wrapped inside the Layout component for consistent navigation
 *
 * Key Features:
 * - AuthProvider for global authentication state
 * - Protected routes based on authentication status
 * - Centralized routing configuration
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import DocumentAnalyzer from './pages/DocumentAnalyzer';
import SpeechAnalyzer from './pages/SpeechAnalyzer';
import PracticeMode from './pages/PracticeMode';
import Analytics from './pages/Analytics';
import LiveCoach from './pages/LiveCoach';
import Login from './pages/Login';
import PresentationRewriter from './pages/PresentationRewriter';
import PresentationGenerator from './pages/PresentationGenerator';
import Download from './pages/Download';
import './App.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>

            {/* Public Login Route */}
            <Route path="/login" element={<Login />} />

            {/* Protected Routes */}
            <Route element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>

              {/* Default Route */}
              <Route path="/" element={<Navigate to="/analytics" replace />} />

              {/* Document Analyzer */}
              <Route path="/analyzer" element={<ErrorBoundary><DocumentAnalyzer /></ErrorBoundary>} />

              {/* Speech Analyzer */}
              <Route path="/speech" element={<ErrorBoundary><SpeechAnalyzer /></ErrorBoundary>} />

              {/* Live Coach */}
              <Route path="/live-coach" element={<ErrorBoundary><LiveCoach /></ErrorBoundary>} />

              {/* AI Coach */}
              <Route path="/practice" element={<ErrorBoundary><PracticeMode /></ErrorBoundary>} />

              {/* Presentation Rewriter */}
              <Route
                path="/presentation-rewriter"
                element={<ErrorBoundary><PresentationRewriter /></ErrorBoundary>}
              />

              {/* Presentation Generator */}
              <Route
                path="/presentation-generator"
                element={<ErrorBoundary><PresentationGenerator /></ErrorBoundary>}
              />

              {/* Download App */}
              <Route path="/download" element={<ErrorBoundary><Download /></ErrorBoundary>} />

              {/* Analytics */}
              <Route path="/analytics" element={<ErrorBoundary><Analytics /></ErrorBoundary>} />

            </Route>

            {/* Catch-all Wildcard Route */}
            <Route path="*" element={<Navigate to="/analytics" replace />} />

          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;