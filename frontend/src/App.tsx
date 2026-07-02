import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Landing from './pages/Landing'
import Deals from './pages/Deals'
import Report from './pages/Report'
import { DocViewerProvider } from './context/DocViewerContext'
import DocViewer from './components/DocViewer'

export default function App() {
  return (
    <BrowserRouter>
      <DocViewerProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/deals" element={<Deals />} />
          <Route path="/report" element={<Report />} />
        </Routes>
        <DocViewer />
      </DocViewerProvider>
    </BrowserRouter>
  )
}
