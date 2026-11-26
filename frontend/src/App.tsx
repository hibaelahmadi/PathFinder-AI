
import './App.css'
import Header from './components/layout/Header'
import ProfileSummary from './components/profile/ProfileSummary'
import ChatPanel from './components/chat/ChatPanel'
import Dashboard from './components/dashboard/Dashboard'

function App() {
  return (
      <div className="app-container">
        <Header isAuthenticated={false} />

        <ProfileSummary />

        <main className="main-layout">
          <ChatPanel />
          <Dashboard />
        </main>

        <footer className="app-footer">
          <p>PathFinder AI · Academic orientation for Moroccan students</p>
        </footer>
      </div>
  )
}

export default App
