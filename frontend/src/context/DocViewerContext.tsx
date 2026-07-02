import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import type { ReportDocument } from '../types/report'

interface DocViewerState {
  document: ReportDocument | null
  page: number
}

interface DocViewerContextValue extends DocViewerState {
  openDoc: (doc: ReportDocument, page: number) => void
  close: () => void
}

const DocViewerContext = createContext<DocViewerContextValue | null>(null)

export function DocViewerProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DocViewerState>({ document: null, page: 1 })

  const openDoc = useCallback((doc: ReportDocument, page: number) => {
    setState({ document: doc, page })
  }, [])

  const close = useCallback(() => {
    setState({ document: null, page: 1 })
  }, [])

  const value = useMemo(
    () => ({ ...state, openDoc, close }),
    [state, openDoc, close],
  )

  return <DocViewerContext.Provider value={value}>{children}</DocViewerContext.Provider>
}

export function useDocViewer(): DocViewerContextValue {
  const ctx = useContext(DocViewerContext)
  if (!ctx) throw new Error('useDocViewer must be used within DocViewerProvider')
  return ctx
}
