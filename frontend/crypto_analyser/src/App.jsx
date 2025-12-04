
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-8">
      <h1 className="text-4xl font-bold mb-6">
        <span className="text-blue-400">AI</span> Crypto Analyzer v4
      </h1>
      
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
        <p className="text-lg mb-4">
          Tailwind CSS 4.0 është instaluar me sukses! 🎉
        </p>
        
        <div className="flex gap-4 mb-6">
          <button className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg transition">
            Dashboard
          </button>
          <button className="bg-purple-500 hover:bg-purple-600 px-4 py-2 rounded-lg transition">
            Analytics
          </button>
          <button className="bg-emerald-500 hover:bg-emerald-600 px-4 py-2 rounded-lg transition">
            Portfolio
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 p-4 rounded-xl">
            <h3 className="font-semibold">BTC</h3>
            <p className="text-2xl">$42,156.30</p>
            <p className="text-green-400">+2.4%</p>
          </div>
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-4 rounded-xl">
            <h3 className="font-semibold">ETH</h3>
            <p className="text-2xl">$2,845.20</p>
            <p className="text-green-400">+1.8%</p>
          </div>
          <div className="bg-gradient-to-r from-emerald-500/20 to-teal-500/20 p-4 rounded-xl">
            <h3 className="font-semibold">SOL</h3>
            <p className="text-2xl">$98.45</p>
            <p className="text-red-400">-0.5%</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
