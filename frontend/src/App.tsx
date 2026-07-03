import { HashRouter, Route, Routes } from 'react-router-dom'
import Landing from './pages/Landing'
import Deals from './pages/Deals'
import DealWorkspace from './pages/DealWorkspace'
import Report from './pages/Report'
import Login from './pages/Login'
import { AuthProvider } from './context/AuthContext'
import { DocViewerProvider } from './context/DocViewerContext'
import DocViewer from './components/DocViewer'
import RequireAuth from './components/RequireAuth'

export default function App() {
  return (
    <HashRouter>
      <AuthProvider>
        <DocViewerProvider>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/report" element={<Report />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/deals"
              element={
                <RequireAuth>
                  <Deals />
                </RequireAuth>
              }
            />
            <Route
              path="/deals/:id"
              element={
                <RequireAuth>
                  <DealWorkspace />
                </RequireAuth>
              }
            />
          </Routes>
          <DocViewer />
        </DocViewerProvider>
      </AuthProvider>
    </HashRouter>
  )
}
