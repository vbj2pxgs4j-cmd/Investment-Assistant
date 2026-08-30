import React, { useState, useEffect, useRef } from 'react';
import ComplianceBanner from './components/ComplianceBanner';
import Navbar from './components/Navbar';
import StarterChips from './components/StarterChips';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import SchemeExplorer from './components/SchemeExplorer';
import TelemetryModal from './components/TelemetryModal';
import { sendChatQuery, fetchSchemes, fetchHealth } from './services/api';
import { executeClientRAG } from './services/clientRAGEngine';

const FALLBACK_SCHEMES = [
  {
    scheme_code: 'hdfc-mid-cap-fund-direct-growth',
    scheme_name: 'HDFC Mid-Cap Opportunities',
    category: 'Equity - Mid Cap',
    riskometer: 'Very High Risk',
    benchmark_index: 'NIFTY Midcap 150 TRI',
    ter: '0.74%',
    source_url: 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
  },
  {
    scheme_code: 'hdfc-small-cap-fund-direct-growth',
    scheme_name: 'HDFC Small Cap Fund',
    category: 'Equity - Small Cap',
    riskometer: 'Very High Risk',
    benchmark_index: 'BSE 250 SmallCap TRI',
    ter: '0.68%',
    source_url: 'https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth',
  },
  {
    scheme_code: 'hdfc-large-cap-fund-direct-growth',
    scheme_name: 'HDFC Top 100 Fund',
    category: 'Equity - Large Cap',
    riskometer: 'Very High Risk',
    benchmark_index: 'NIFTY 100 TRI',
    ter: '1.08%',
    source_url: 'https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth',
  },
  {
    scheme_code: 'hdfc-elss-tax-saver-fund-direct-plan-growth',
    scheme_name: 'HDFC ELSS Tax Saver',
    category: 'Equity - ELSS',
    riskometer: 'Very High Risk',
    benchmark_index: 'NIFTY 500 TRI',
    ter: '1.15%',
    source_url: 'https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth',
  },
  {
    scheme_code: 'hdfc-gold-etf-fund-of-fund-direct-plan-growth',
    scheme_name: 'HDFC Gold ETF FoF',
    category: 'Other - FoF Dom',
    riskometer: 'High Risk',
    benchmark_index: 'Domestic Price of Gold',
    ter: '0.27%',
    source_url: 'https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth',
  },
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am your facts-only Mutual Fund FAQ Assistant for HDFC schemes. Ask me anything about exit loads, expense ratios (TER), minimum SIP limits, lock-in periods, or statement downloads.',
      status: 'success',
      latency_ms: 120,
      source_url: 'https://groww.in/mutual-funds',
      last_updated: '2024-04-01',
      sentence_count: 2,
      is_fallback: false,
    },
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeScheme, setActiveScheme] = useState('all');
  const [schemes, setSchemes] = useState(FALLBACK_SCHEMES);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [telemetryOpen, setTelemetryOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState({ online: true, latency: '<600ms', indexed: 38 });

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load schemes & health on startup
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [schemesData, healthData] = await Promise.all([
          fetchSchemes().catch(() => null),
          fetchHealth().catch(() => null),
        ]);

        if (schemesData?.schemes && schemesData.schemes.length > 0) {
          setSchemes(schemesData.schemes);
        }

        if (healthData) {
          setHealthStatus({
            online: healthData.status === 'healthy',
            latency: '<600ms',
            indexed: healthData.total_indexed_chunks || 38,
          });
        }
      } catch (err) {
        console.warn('Initial data fetch notice:', err);
      }
    }

    loadInitialData();
  }, []);

  const handleQuerySubmit = async (customQuery) => {
    const query = (customQuery || inputQuery).trim();
    if (!query || loading) return;

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `assistant-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        sender: 'user',
        text: query,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);

    setInputQuery('');
    setLoading(true);

    try {
      const data = await sendChatQuery(query);

      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          sender: 'assistant',
          text: data.response,
          status: data.status,
          intent: data.intent,
          latency_ms: data.latency_ms,
          source_url: data.source_url,
          last_updated: data.last_updated,
          sentence_count: data.sentence_count,
          disclaimer: data.disclaimer,
          is_fallback: data.is_fallback,
        },
      ]);
    } catch (error) {
      console.warn('Chat query fallback engaged:', error);
      const fallbackData = executeClientRAG(query);
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          sender: 'assistant',
          text: fallbackData.response,
          status: fallbackData.status,
          intent: fallbackData.intent,
          latency_ms: fallbackData.latency_ms,
          source_url: fallbackData.source_url,
          last_updated: fallbackData.last_updated,
          sentence_count: fallbackData.sentence_count,
          disclaimer: fallbackData.disclaimer,
          is_fallback: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSchemeSelect = (schemeCode, schemeName) => {
    setActiveScheme(schemeCode);
    if (schemeCode !== 'all' && schemeName) {
      setInputQuery(`What is the expense ratio and exit load for ${schemeName}?`);
    }
  };

  const handleSchemeCardClick = (scheme) => {
    setActiveScheme(scheme.scheme_code);
    setInputQuery(`What is the exit load, lock-in period, and minimum SIP for ${scheme.scheme_name}?`);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-background text-on-surface font-body-sm overflow-hidden select-none">
      {/* 1. Regulatory Compliance Banner */}
      <ComplianceBanner />

      {/* 2. Glassmorphic Navbar */}
      <Navbar
        schemes={schemes}
        activeScheme={activeScheme}
        onSchemeSelect={handleSchemeSelect}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        healthStatus={healthStatus}
        onOpenTelemetry={() => setTelemetryOpen(true)}
      />

      {/* 3. Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Central Chat Stream */}
        <main className="flex-1 flex flex-col relative h-full bg-surface-dim/40 border-r border-outline-variant z-10">
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-36 flex flex-col gap-6">
            {/* Starter Prompt Chips */}
            {messages.length <= 1 && (
              <StarterChips onSelectPrompt={(prompt) => handleQuerySubmit(prompt)} />
            )}

            {/* Message Stream */}
            <div className="flex flex-col gap-5 max-w-4xl mx-auto w-full">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Typing Indicator */}
              {loading && (
                <div className="flex justify-start w-full message-animate">
                  <div className="flex gap-3.5 max-w-[90%] items-center">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/50">
                      <span className="material-symbols-outlined text-primary text-[18px]">robot_2</span>
                    </div>
                    <div className="glass-panel rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
                      <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
                      <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
                      <span className="text-xs text-on-surface-variant ml-2 font-mono-data">
                        Retrieving facts & synthesizing...
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* 4. Bottom Input Bar */}
          <ChatInput
            inputQuery={inputQuery}
            setInputQuery={setInputQuery}
            onSubmit={() => handleQuerySubmit()}
            loading={loading}
          />
        </main>

        {/* 5. Right Sidebar: Scheme Explorer */}
        <SchemeExplorer
          schemes={schemes}
          activeScheme={activeScheme}
          onSchemeClick={handleSchemeCardClick}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
      </div>

      {/* 6. Telemetry & Quota Modal */}
      <TelemetryModal
        isOpen={telemetryOpen}
        onClose={() => setTelemetryOpen(false)}
      />
    </div>
  );
}
