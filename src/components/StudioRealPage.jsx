import { Mic, Square, Trash2, Download, AudioLines, Disc3 } from 'lucide-react'
import { useClipRecorder } from '../hooks/useClipRecorder.js'

// Studio Real — a real recording booth. Records actual microphone audio into
// clips that can play (looped, in sync) over the song. Recordings are
// session-only; download a take to keep it.
export default function StudioRealPage({ recordings, onAdd, onRemove, onTogglePlay }) {
  const { supported, recording, level, elapsed, error, start, stop } = useClipRecorder({ onClip: onAdd })

  return (
    <section className="glass page-pane" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Disc3 size={18} style={{ color: 'var(--neon-pink)' }} />
        <span style={{ fontSize: 17, fontWeight: 700 }}>Studio Real</span>
        <span className="mono" style={{ fontSize: 9, color: 'var(--text-faint)', textTransform: 'uppercase' }}>recording booth</span>
      </div>

      <p style={{ color: 'var(--text-dim)', fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
        Record your real voice or instrument through the mic. Each take can play <strong>over your song</strong> in
        the Studio. (Recordings are kept for this session — download any you want to keep.)
      </p>

      {/* Record control */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
        <button
          type="button"
          onClick={() => (recording ? stop() : start())}
          disabled={!supported}
          aria-label={recording ? 'Stop recording' : 'Start recording'}
          style={{
            width: 92,
            height: 92,
            borderRadius: '50%',
            display: 'grid',
            placeItems: 'center',
            cursor: supported ? 'pointer' : 'not-allowed',
            border: `2px solid ${recording ? '#ff0000' : 'rgba(255,0,0,0.5)'}`,
            background: recording
              ? `radial-gradient(circle, rgba(255,0,0,${0.25 + level * 0.5}), rgba(255,0,0,0.08))`
              : 'radial-gradient(circle, rgba(255,0,0,0.18), rgba(62,166,255,0.08))',
            color: recording ? '#ff5252' : 'var(--neon-pink)',
            transition: 'background 80ms linear',
            opacity: supported ? 1 : 0.45,
          }}
        >
          {recording ? <Square size={30} /> : <Mic size={34} />}
        </button>
        <div className="mono" style={{ fontSize: 11, color: recording ? '#ff5252' : 'var(--text-faint)' }}>
          {!supported
            ? 'Mic not available here'
            : recording
              ? `● REC  ${elapsed.toFixed(1)}s`
              : 'Tap to record'}
        </div>
        {error && error !== 'no-speech' && (
          <span className="mono" style={{ fontSize: 10, color: '#ff5252' }}>mic: {error}</span>
        )}
      </div>

      {/* Recordings */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {recordings.length === 0 ? (
          <div style={{ padding: '20px 12px', textAlign: 'center', color: 'var(--text-faint)', fontSize: 13 }}>
            No takes yet. Hit the mic to record one.
          </div>
        ) : (
          recordings.map((rec) => (
            <div
              key={rec.id}
              style={{ padding: 12, borderRadius: 12, background: 'rgba(10,10,16,0.55)', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 10 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <AudioLines size={15} style={{ color: 'var(--neon-pink)' }} />
                <span style={{ fontSize: 13.5, fontWeight: 700 }}>{rec.name}</span>
                <span className="mono" style={{ fontSize: 10, color: 'var(--text-faint)' }}>{rec.duration.toFixed(1)}s</span>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                  <a
                    href={rec.url}
                    download={`${rec.name}.webm`}
                    title="Download"
                    style={{ width: 30, height: 30, borderRadius: 7, display: 'grid', placeItems: 'center', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
                  >
                    <Download size={14} />
                  </a>
                  <button
                    onClick={() => onRemove(rec.id)}
                    title="Delete"
                    style={{ width: 30, height: 30, borderRadius: 7, display: 'grid', placeItems: 'center', border: '1px solid var(--border)', background: 'transparent', color: '#ff5252', cursor: 'pointer' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              <audio src={rec.url} controls style={{ width: '100%', height: 34 }} />

              <button
                type="button"
                onClick={() => onTogglePlay(rec.id)}
                className="mono"
                style={{
                  alignSelf: 'flex-start',
                  fontSize: 11,
                  padding: '6px 10px',
                  borderRadius: 8,
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  background: rec.playWithSong ? 'rgba(43,166,64,0.12)' : 'rgba(255,255,255,0.05)',
                  border: `1px solid ${rec.playWithSong ? 'var(--neon-green)' : 'var(--border)'}`,
                  color: rec.playWithSong ? 'var(--neon-green)' : 'var(--text-dim)',
                }}
              >
                {rec.playWithSong ? '● Plays with song' : 'Play with song'}
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  )
}
