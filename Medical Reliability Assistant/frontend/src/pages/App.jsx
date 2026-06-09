import { useState, useEffect } from 'react'
import { Home, Search, BarChart2, Info, Mail, LifeBuoy, LogIn } from 'lucide-react'
import HomePage from '../components/HomePage.jsx'
import ChatInterface from '../components/ChatInterface.jsx'
import DeviceHealthDashboard from '../components/DeviceHealthDashboard.jsx'
import TechStack from '../components/TechStack.jsx'
import ContactPage from '../components/ContactPage.jsx'
import SupportPage from '../components/SupportPage.jsx'
import LoginModal from '../components/LoginModal.jsx'
import { LogoFull } from '../components/Logo.jsx'
import { fetchHealth } from '../utils/api.js'

const TABS = [
  { id: 'home',      label: 'Home',            icon: Home },
  { id: 'query',     label: 'Query Assistant', icon: Search },
  { id: 'dashboard', label: 'Device Health',   icon: BarChart2 },
  { id: 'about',     label: 'About Me',        icon: Info },
  { id: 'contact',   label: 'Contact',         icon: Mail },
  { id: 'support',   label: 'Support',         icon: LifeBuoy },
]

const PAGE_META = {
  query:     { title: 'Equipment Reliability Query',  desc: 'Describe an equipment issue in natural language. The multi-agent system will retrieve historical incidents, detect anomalies, and generate explainable recommendations.' },
  dashboard: { title: 'Device Health Dashboard',      desc: 'Aggregated failure rates across all equipment types from the ingested dataset.' },
  about:     { title: 'About Me',                     desc: 'Complete architecture of the multi-agent reliability assistant — runtime, agents, retrieval, data pipeline, and infrastructure.' },
  contact:   { title: 'Contact Us',                   desc: 'Get in touch with the DR. BLEEP engineering support team.' },
  support:   { title: 'Help & Support',               desc: 'Documentation, FAQs, and system status for biomedical engineers.' },
}

export default function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [showLogin, setShowLogin] = useState(false)

  useEffect(() => { fetchHealth().catch(() => {}) }, [])

  const isHome = activeTab === 'home'

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <LogoFull inverted />
        <div className="header-actions">
          <button className="header-sign-in" onClick={() => setShowLogin(true)}>
            <LogIn size={14} /> Sign In
          </button>
        </div>
      </header>

      {/* Nav */}
      <nav className="nav">
        <div className="nav-primary">
          {TABS.filter(t => !['contact','support'].includes(t.id)).map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                className={`nav-tab${activeTab === tab.id ? ' active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={14} />{tab.label}
              </button>
            )
          })}
        </div>
        <div className="nav-secondary">
          {TABS.filter(t => ['contact','support'].includes(t.id)).map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                className={`nav-tab${activeTab === tab.id ? ' active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={14} />{tab.label}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Main */}
      <main className={`app-main${isHome ? '' : ' app-main-pad'}`}>
        <div className={isHome ? '' : 'page-content'}>

          {activeTab === 'home' && (
            <div className="fade-in">
              <HomePage onNavigate={setActiveTab} />
            </div>
          )}

          {activeTab !== 'home' && (
            <div className="fade-in">
              <div className="page-header">
                <h2>{PAGE_META[activeTab]?.title}</h2>
                <p>{PAGE_META[activeTab]?.desc}</p>
                <div className="page-header-accent" />
              </div>

              {activeTab === 'query'     && <ChatInterface />}
              {activeTab === 'dashboard' && <div className="dashboard-card"><DeviceHealthDashboard /></div>}
              {activeTab === 'about'     && <TechStack />}
              {activeTab === 'contact'   && <ContactPage />}
              {activeTab === 'support'   && <SupportPage />}
            </div>
          )}
        </div>
      </main>

      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </div>
  )
}
