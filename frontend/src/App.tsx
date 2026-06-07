import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API = 'http://127.0.0.1:8000'

const MOODS = ['happy', 'sad', 'angry', 'chill', 'energetic', 'romantic', 'dance', 'focus']
const GENRES = ['pop', 'rock', 'hip-hop', 'jazz', 'classical', 'country', 
                'electronic', 'r-n-b', 'indie', 'metal', 'folk', 'blues']

interface Track {
  track_name: string
  artists: string
  track_genre: string
  popularity: number
  similarity_score: number
}

function App() {
  // Mode: 'song' or 'mood'
  const [mode, setMode] = useState<'song' | 'mood'>('song')

  // Song mode state
  const [songName, setSongName] = useState('')

  // Mood mode state
  const [mood, setMood] = useState('')
  const [genre, setGenre] = useState('')
  const [englishOnly, setEnglishOnly] = useState(false)

  // Shared state
  const [results, setResults] = useState<Track[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const recommendBySong = async () => {
    if (!songName.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await axios.post(`${API}/recommend/song`, {
        song_name: songName,
        n: 10
      })
      setResults(res.data.recommendations)
    } catch (e) {
      setError('Song not found. Try another title!')
    }
    setLoading(false)
  }

  const recommendByMood = async () => {
    if (!mood) return
    setLoading(true)
    setError('')
    try {
      const res = await axios.post(`${API}/recommend/mood`, {
        mood,
        genre: genre || null,
        english_only: englishOnly,
        n: 10
      })
      setResults(res.data.recommendations)
    } catch (e) {
      setError('No songs found for those filters. Try different options!')
    }
    setLoading(false)
  }

  return (
    <div className="app">
      <h1>🎵 Music Recommender</h1>

      {/* Mode Toggle */}
      <div className="mode-toggle">
        <button
          className={mode === 'song' ? 'active' : ''}
          onClick={() => { setMode('song'); setResults([]); setError('') }}
        >
          By Song
        </button>
        <button
          className={mode === 'mood' ? 'active' : ''}
          onClick={() => { setMode('mood'); setResults([]); setError('') }}
        >
          By Mood
        </button>
      </div>

      {/* Song Mode */}
      {mode === 'song' && (
        <div className="form">
          <input
            type="text"
            placeholder="Enter a song name..."
            value={songName}
            onChange={e => setSongName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && recommendBySong()}
          />
          <button onClick={recommendBySong} disabled={loading}>
            {loading ? 'Finding...' : 'Get Recommendations'}
          </button>
        </div>
      )}

      {/* Mood Mode */}
      {mode === 'mood' && (
        <div className="form">
          <div className="mood-grid">
            {MOODS.map(m => (
              <button
                key={m}
                className={`mood-btn ${mood === m ? 'active' : ''}`}
                onClick={() => setMood(m)}
              >
                {m}
              </button>
            ))}
          </div>

          <select value={genre} onChange={e => setGenre(e.target.value)}>
            <option value="">Any genre</option>
            {GENRES.map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={englishOnly}
              onChange={e => setEnglishOnly(e.target.checked)}
            />
            English songs only
          </label>

          <button onClick={recommendByMood} disabled={loading || !mood}>
            {loading ? 'Finding...' : 'Get Recommendations'}
          </button>
        </div>
      )}

      {/* Error */}
      {error && <p className="error">{error}</p>}

      {/* Results */}
      {results.length > 0 && (
        <div className="results">
          <h2>Recommendations</h2>
          {results.map((track, i) => (
            <div key={i} className="track-card">
              <div className="track-info">
                <span className="track-name">{track.track_name}</span>
                <span className="track-artist">{track.artists}</span>
              </div>
              <div className="track-meta">
                <span className="genre-tag">{track.track_genre}</span>
                <span className="score">Match: {(track.similarity_score * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App