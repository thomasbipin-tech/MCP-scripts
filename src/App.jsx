import { useCallback, useEffect, useRef, useState } from 'react'
import { Music4, Menu, X } from 'lucide-react'
import VoicePanel from './components/VoicePanel.jsx'
import HumRecorder from './components/HumRecorder.jsx'
import StructureEditor from './components/StructureEditor.jsx'
import TrackMixer from './components/TrackMixer.jsx'
import AICollabPanel from './components/AICollabPanel.jsx'
import Transport from './components/Transport.jsx'
import SettingsBar from './components/SettingsBar.jsx'
import Sidebar from './components/Sidebar.jsx'
import LyricsPage from './components/LyricsPage.jsx'
import SuperGeneratePage from './components/SuperGeneratePage.jsx'
import InstrumentsPage from './components/InstrumentsPage.jsx'
import { getEngine } from './lib/audioEngine.js'
import { interpretCommand, generateSurpriseSong, usingLiveAI } from './lib/aiProducer.js'
import { DEFAULT_SONG_STATE, makeTrack, NEON_COLORS, INSTRUMENTS } from './lib/constants.js'

const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n))

// ----- Autosave (localStorage) -----
const SONG_KEY = 'ai-music-studio:songState:v1'
const PAGE_KEY = 'ai-music-studio:page:v1'

function loadSong() {
  try {
    const raw = localStorage.getItem(SONG_KEY)
    if (raw) return { ...DEFAULT_SONG_STATE, ...JSON.parse(raw) }
  } catch {
    /* ignore corrupt/blocked storage */
  }
  return DEFAULT_SONG_STATE
}

export default function App() {
  const [songState, setSongState] = useState(loadSong)
  const [page, setPage] = useState(() => {
    const saved = localStorage.getItem(PAGE_KEY)
    return ['lyrics', 'super', 'sounds'].includes(saved) ? saved : 'studio'
  })
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigate = useCallback((p) => {
    setPage(p)
    setSidebarOpen(false)
  }, [])
  const [aiLog, setAiLog] = useState([])
  const [thinking, setThinking] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [selectedTrackId, setSelectedTrackId] = useState(null)
  const [selectedSegment, setSelectedSegment] = useState(null)

  const engine = getEngine()
  const songStateRef = useRef(songState)
  songStateRef.current = songState

  // Persist song state + active page so nothing is lost on reload.
  useEffect(() => {
    try {
      localStorage.setItem(SONG_KEY, JSON.stringify(songState))
    } catch {
      /* ignore */
    }
  }, [songState])

  useEffect(() => {
    try {
      localStorage.setItem(PAGE_KEY, page)
    } catch {
      /* ignore */
    }
  }, [page])

  // Keep the audio engine in sync with the latest song state (live edits).
  useEffect(() => {
    engine.setSongState(songState)
  }, [songState, engine])

  // Drive the playhead while playing.
  useEffect(() => {
    if (!playing) return
    let raf
    const tick = () => {
      setProgress(engine.getProgress())
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [playing, engine])

  useEffect(() => () => engine.dispose(), [engine])

  // ----- Change merging -----
  const applyChanges = useCallback((changes) => {
    if (!changes || !Object.keys(changes).length) return
    setSongState((prev) => ({ ...prev, ...changes }))
  }, [])

  // ----- Command dispatch (voice + text) -----
  const runCommand = useCallback(
    async (command) => {
      if (!command) return
      setAiLog((l) => [...l, { role: 'user', command }])
      setThinking(true)
      try {
        const res = await interpretCommand(command, songStateRef.current, {
          selectedTrackId,
          selectedSegment,
        })
        applyChanges(res.changes)
        setAiLog((l) => [...l, { role: 'ai', ...res }])
      } catch (err) {
        setAiLog((l) => [
          ...l,
          { role: 'ai', message: `Something went wrong: ${err.message}`, tip: '', nextSuggestion: '' },
        ])
      } finally {
        setThinking(false)
      }
    },
    [applyChanges, selectedTrackId, selectedSegment],
  )

  const handleSurprise = useCallback(async () => {
    setAiLog((l) => [...l, { role: 'user', command: 'Surprise me' }])
    setThinking(true)
    await new Promise((r) => setTimeout(r, 450))
    const res = generateSurpriseSong(songStateRef.current)
    applyChanges(res.changes)
    setAiLog((l) => [...l, { role: 'ai', ...res }])
    setSelectedSegment(null)
    setSelectedTrackId(null)
    setThinking(false)
  }, [applyChanges])

  // ----- Track mutations -----
  const updateTrack = useCallback((id, patch) => {
    setSongState((p) => ({
      ...p,
      tracks: p.tracks.map((t) => (t.id === id ? { ...t, ...patch } : t)),
    }))
  }, [])

  const toggleEffect = useCallback((id, fx) => {
    setSongState((p) => ({
      ...p,
      tracks: p.tracks.map((t) =>
        t.id === id ? { ...t, effects: { ...t.effects, [fx]: !t.effects[fx] } } : t,
      ),
    }))
  }, [])

  const deleteTrack = useCallback(
    (id) => {
      setSongState((p) => ({ ...p, tracks: p.tracks.filter((t) => t.id !== id) }))
      if (selectedTrackId === id) setSelectedTrackId(null)
    },
    [selectedTrackId],
  )

  const reorderTracks = useCallback((next) => {
    setSongState((p) => ({ ...p, tracks: next }))
  }, [])

  const addTrackFromHum = useCallback((notes, instrument) => {
    setSongState((p) => {
      const color = NEON_COLORS[p.tracks.length % NEON_COLORS.length]
      const name = INSTRUMENTS.find((i) => i.id === instrument)?.name || 'Melody'
      const track = makeTrack({ instrument, color, notes, name })
      return { ...p, tracks: [...p.tracks, track] }
    })
    setAiLog((l) => [
      ...l,
      {
        role: 'ai',
        message: `Added your hummed melody as a ${instrument} track.`,
        tip: 'Double the melody an octave up on another instrument to thicken the hook.',
        nextSuggestion: 'Hit play, or say “add reverb to ' + instrument + '”.',
      },
    ])
  }, [])

  const previewMelody = useCallback(
    (notes, instrument) => {
      engine.previewMelody(notes, instrument)
    },
    [engine],
  )

  // ----- Structure mutations -----
  const reorderStructure = useCallback((next) => {
    setSongState((p) => ({ ...p, structure: next }))
  }, [])

  const changeRepeat = useCallback((index, delta) => {
    setSongState((p) => ({
      ...p,
      structure: p.structure.map((s, i) =>
        i === index ? { ...s, repeat: clamp((s.repeat || 1) + delta, 1, 8) } : s,
      ),
    }))
  }, [])

  const updateLyrics = useCallback((text) => {
    setSongState((p) => ({ ...p, lyrics: text }))
  }, [])

  const changeInstrument = useCallback((id, instrument) => {
    setSongState((p) => ({
      ...p,
      tracks: p.tracks.map((t) =>
        t.id === id
          ? { ...t, instrument, name: INSTRUMENTS.find((x) => x.id === instrument)?.name || t.name }
          : t,
      ),
    }))
  }, [])

  const applyVariation = useCallback(
    (changes) => {
      applyChanges(changes)
      setSelectedSegment(null)
      setSelectedTrackId(null)
      setPage('studio')
      setAiLog((l) => [
        ...l,
        {
          role: 'ai',
          message: `Loaded a ${changes.mood} ${changes.genre} version in ${changes.key}.`,
          tip: 'Hit play to hear it — real instruments load on the first play.',
          nextSuggestion: 'Tweak the step grids, or Super Generate again for more options.',
        },
      ])
    },
    [applyChanges],
  )

  // ----- Playback -----
  const handlePlay = useCallback(async () => {
    await engine.play()
    setPlaying(true)
  }, [engine])

  const handlePause = useCallback(() => {
    engine.pause()
    setPlaying(false)
  }, [engine])

  const handleStop = useCallback(() => {
    engine.stop()
    setPlaying(false)
    setProgress(0)
  }, [engine])

  const setBpm = useCallback((v) => applyChanges({ bpm: clamp(v, 40, 240) }), [applyChanges])
  const setMaster = useCallback((v) => applyChanges({ masterVolume: clamp(v, 0, 100) }), [applyChanges])

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <button
            type="button"
            className="menu-btn"
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={sidebarOpen}
            onClick={() => setSidebarOpen((v) => !v)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="brand-mark">
            <Music4 size={22} />
          </div>
          <div>
            <div className="brand-title">AI MUSIC STUDIO</div>
            <div className="mono" style={{ fontSize: 9.5, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.18em' }}>
              GarageBand style AI DAW
            </div>
          </div>
        </div>
        <SettingsBar songState={songState} onChange={applyChanges} onSurprise={handleSurprise} thinking={thinking} />
      </header>

      <div className="app-body">
        {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />}
        <Sidebar page={page} onNavigate={navigate} open={sidebarOpen} />

        <div className="page-area">
          {page === 'studio' && (
            <div className="studio-grid">
              <div className="left-col">
                <VoicePanel onCommand={runCommand} thinking={thinking} liveAI={usingLiveAI} />
                <HumRecorder songState={songState} onAddTrack={addTrackFromHum} onPreview={previewMelody} />
                <StructureEditor
                  songState={songState}
                  selectedSegment={selectedSegment}
                  onSelectSegment={setSelectedSegment}
                  onReorder={reorderStructure}
                  onRepeat={changeRepeat}
                  progress={progress}
                />
                <TrackMixer
                  tracks={songState.tracks}
                  playing={playing}
                  structure={songState.structure}
                  songKey={songState.key}
                  selectedTrackId={selectedTrackId}
                  onSelect={setSelectedTrackId}
                  onUpdate={updateTrack}
                  onToggleEffect={toggleEffect}
                  onDelete={deleteTrack}
                  onReorder={reorderTracks}
                />
              </div>

              <aside className="right-col">
                <AICollabPanel log={aiLog} onCommand={runCommand} thinking={thinking} />
              </aside>
            </div>
          )}

          {page === 'lyrics' && <LyricsPage songState={songState} onChange={updateLyrics} />}

          {page === 'super' && <SuperGeneratePage songState={songState} onApply={applyVariation} />}

          {page === 'sounds' && <InstrumentsPage songState={songState} onChangeInstrument={changeInstrument} />}
        </div>
      </div>

      <Transport
        playing={playing}
        onPlay={handlePlay}
        onPause={handlePause}
        onStop={handleStop}
        bpm={songState.bpm}
        onBpmChange={setBpm}
        masterVolume={songState.masterVolume ?? 80}
        onMasterChange={setMaster}
        getSpectrum={() => engine.getSpectrum()}
        progress={progress}
        songState={songState}
      />
    </div>
  )
}
