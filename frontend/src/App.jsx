import { useState, useEffect } from 'react'

function App() {
  const [file, setFile] = useState(null)
  const [scanId, setScanId] = useState(null)
  const [scanStatus, setScanStatus] = useState(null)
  const [error, setError] = useState('')

  const handleStartScan = async (e) => {
    e.preventDefault()
    if (!file) {
      setError("Please select a Postman or OpenAPI JSON file.")
      return
    }
    setError('')
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      // Assuming backend is at localhost:8000
      const res = await fetch('http://localhost:8000/scans', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setScanId(data.scan_id)
    } catch (err) {
      setError("Failed to start scan. Is the backend running?")
    }
  }

  useEffect(() => {
    if (!scanId) return
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/scans/${scanId}`)
        const data = await res.json()
        setScanStatus(data)
        if (data.status === 'completed' || data.status.startsWith('failed')) {
          clearInterval(interval)
        }
      } catch (err) {
        console.error(err)
      }
    }, 1000)
    
    return () => clearInterval(interval)
  }, [scanId])

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">
            APIShield
          </h1>
          <p className="text-slate-400 text-lg">Automated REST API Security Testing</p>
        </header>
        
        {!scanId && (
          <div className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700">
            <h2 className="text-2xl font-bold mb-6 text-emerald-400">Start a New Scan</h2>
            <form onSubmit={handleStartScan} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Upload Collection/Spec (JSON)</label>
                <input 
                  type="file" 
                  accept=".json"
                  onChange={e => setFile(e.target.files[0])}
                  className="block w-full text-sm text-slate-400
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-emerald-500 file:text-white
                    hover:file:bg-emerald-600
                    cursor-pointer bg-slate-700 rounded-md border border-slate-600"
                />
              </div>
              
              <div className="flex items-center space-x-3">
                <input type="checkbox" required id="consent" className="w-5 h-5 accent-emerald-500" />
                <label htmlFor="consent" className="text-sm text-slate-400">
                  I confirm I am authorized to scan this target API.
                </label>
              </div>

              {error && <p className="text-red-400 text-sm">{error}</p>}
              
              <button 
                type="submit"
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-bold py-3 px-4 rounded-lg shadow-lg transform transition hover:-translate-y-0.5"
              >
                Launch Security Scan
              </button>
            </form>
          </div>
        )}

        {scanStatus && (
          <div className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-blue-400">Scan Status</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-bold ${scanStatus.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                {scanStatus.status.toUpperCase()}
              </span>
            </div>
            
            <div className="w-full bg-slate-700 rounded-full h-4 mb-8 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-blue-500 to-emerald-500 h-4 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${scanStatus.progress}%` }}
              ></div>
            </div>

            {scanStatus.status === 'completed' && (
              <div>
                <h3 className="text-xl font-bold mb-4 border-b border-slate-700 pb-2">Vulnerabilities Found: {scanStatus.findings.length}</h3>
                <div className="space-y-6 mt-4">
                  {scanStatus.findings.map((f, i) => (
                    <div key={i} className="bg-slate-900 rounded-lg p-5 border border-red-500/30 shadow-inner">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="text-lg font-bold text-red-400">{f.test_name}</h4>
                        <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded uppercase tracking-wider">
                          {f.severity}
                        </span>
                      </div>
                      <p className="text-slate-300 font-mono text-sm mb-4 bg-slate-800 p-2 rounded">
                        {f.method} {f.endpoint}
                      </p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-4">
                        <div className="bg-slate-800 p-3 rounded border border-slate-700 overflow-x-auto">
                          <span className="block text-xs text-slate-500 uppercase font-bold mb-1">Evidence Request</span>
                          <pre className="text-slate-300">{f.evidence_request}</pre>
                        </div>
                        <div className="bg-slate-800 p-3 rounded border border-slate-700 overflow-x-auto">
                          <span className="block text-xs text-slate-500 uppercase font-bold mb-1">Evidence Response</span>
                          <pre className="text-slate-400">{f.evidence_response}</pre>
                        </div>
                      </div>
                      
                      <div className="bg-blue-900/20 p-3 rounded border border-blue-500/30">
                        <span className="block text-xs text-blue-400 uppercase font-bold mb-1">Remediation</span>
                        <p className="text-blue-100">{f.remediation}</p>
                      </div>
                    </div>
                  ))}
                  
                  {scanStatus.findings.length === 0 && (
                    <div className="text-center p-8 bg-emerald-900/20 rounded-lg border border-emerald-500/30">
                      <p className="text-emerald-400 font-bold text-xl">✅ No vulnerabilities found!</p>
                      <p className="text-emerald-200 mt-2">Your API passed all security tests.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
