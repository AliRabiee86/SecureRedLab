/**
 * SecureRedLab - Main Application Component
 * Phase 8.1 - React Router & Layout Setup
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useThemeStore } from './stores'
import MainLayout from './components/layout/MainLayout'
import DashboardPage from './pages/Dashboard/DashboardPage'
import ScansPage from './pages/Scans/ScansPage'
import AttacksPage from './pages/Attacks/AttacksPage'
import ReportsPage from './pages/Reports/ReportsPage'
import SettingsPage from './pages/Settings/SettingsPage'
import AgenticPage from './pages/Agentic/AgenticPage'

function App() {
  // Initialize theme
  const theme = useThemeStore((state) => state.theme)

  return (
    <div className={`app ${theme}`}>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="scans" element={<ScansPage />} />
          <Route path="attacks" element={<AttacksPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="agentic" element={<AgenticPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </div>
  )
}

export default App
