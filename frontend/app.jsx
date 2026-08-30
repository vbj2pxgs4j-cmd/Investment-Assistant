/**
 * HDFC Mutual Fund FAQ Assistant - React Frontend Application
 * Luminous Fintech Design System (Google Stitch Export Integration)
 */

const { useState, useEffect, useRef } = React;

// Fallback schemes metadata if backend is offline initially
const FALLBACK_SCHEMES = [
  {
    scheme_code: "hdfc-mid-cap-fund-direct-growth",
    scheme_name: "HDFC Mid-Cap Opportunities",
    category: "Equity - Mid Cap",
    riskometer: "Very High Risk",
    benchmark_index: "NIFTY Midcap 150 TRI",
    ter: "0.74%",
    source_url: "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
  },
  {
    scheme_code: "hdfc-small-cap-fund-direct-growth",
    scheme_name: "HDFC Small Cap Fund",
    category: "Equity - Small Cap",
    riskometer: "Very High Risk",
    benchmark_index: "BSE 250 SmallCap TRI",
    ter: "0.68%",
    source_url: "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
  },
  {
    scheme_code: "hdfc-large-cap-fund-direct-growth",
    scheme_name: "HDFC Top 100 Fund",
    category: "Equity - Large Cap",
    riskometer: "Very High Risk",
    benchmark_index: "NIFTY 100 TRI",
    ter: "1.08%",
    source_url: "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
  },
  {
    scheme_code: "hdfc-elss-tax-saver-fund-direct-plan-growth",
    scheme_name: "HDFC ELSS Tax Saver",
    category: "Equity - ELSS",
    riskometer: "Very High Risk",
    benchmark_index: "NIFTY 500 TRI",
    ter: "1.15%",
    source_url: "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
  },
  {
    scheme_code: "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    scheme_name: "HDFC Gold ETF FoF",
    category: "Other - FoF Dom",
    riskometer: "High Risk",
    benchmark_index: "Domestic Price of Gold",
    ter: "0.27%",
    source_url: "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
  },
];

const STARTER_PROMPTS = [
  {
    icon: "bar_chart",
    label: "What is the exit load for HDFC Small Cap Fund?",
    scheme: "hdfc-small-cap-fund-direct-growth",
  },
  {
    icon: "lock",
    label: "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
    scheme: "hdfc-elss-tax-saver-fund-direct-plan-growth",
  },
  {
    icon: "payments",
    label: "What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
    scheme: "hdfc-mid-cap-fund-direct-growth",
  },
  {
    icon: "percent",
    label: "What is the Total Expense Ratio (TER) of HDFC Top 100 Fund?",
    scheme: "hdfc-large-cap-fund-direct-growth",
  },
  {
    icon: "description",
    label: "How do I download my mutual fund capital gains statement?",
    scheme: null,
  },
];

function App() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am your facts-only Mutual Fund FAQ Assistant for HDFC schemes. Ask me anything about exit loads, expense ratios (TER), minimum SIP limits, lock-in periods, or statement downloads.",
      status: "success",
      latency_ms: 120,
      source_url: "https://groww.in/mutual-funds",
      last_updated: "2024-04-01",
      sentence_count: 2,
      is_fallback: false,
    },
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeScheme, setActiveScheme] = useState("all");
  const [schemes, setSchemes] = useState(FALLBACK_SCHEMES);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState({ online: true, latency: "<600ms", indexed: 38 });
  const [copiedId, setCopiedId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Fetch initial schemes and health status on mount
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [schemesRes, healthRes] = await Promise.allSettled([
          fetch("/api/v1/schemes"),
          fetch("/api/v1/health"),
        ]);

        if (schemesRes.status === "fulfilled" && schemesRes.value.ok) {
          const data = await schemesRes.value.json();
          if (data.schemes && data.schemes.length > 0) {
            setSchemes(data.schemes);
          }
        }

        if (healthRes.status === "fulfilled" && healthRes.value.ok) {
          const healthData = await healthRes.value.json();
          setHealthStatus({
            online: healthData.status === "healthy",
            latency: "<600ms",
            indexed: healthData.total_indexed_chunks || 38,
          });
        }
      } catch (err) {
        console.warn("Backend API not yet reachable, using local fallback data:", err);
      }
    }

    loadInitialData();
  }, []);

  // Handle Query Submission
  const handleSubmit = async (queryToSubmit) => {
    const query = (queryToSubmit || inputQuery).trim();
    if (!query || loading) return;

    const userMessageId = "user-" + Date.now();
    const assistantMessageId = "assistant-" + Date.now();

    // Add User Message
    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        sender: "user",
        text: query,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);

    setInputQuery("");
    setLoading(true);

    try {
      const response = await fetch("/api/v1/chat/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Server error occurred");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          sender: "assistant",
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
      console.error("Query dispatch failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          sender: "assistant",
          text: `Unable to connect to the backend server. Please verify the FastAPI backend is running on http://localhost:8000. (${error.message})`,
          status: "error",
          latency_ms: 0,
          source_url: "https://groww.in/mutual-funds",
          last_updated: "2024-04-01",
          sentence_count: 1,
          is_fallback: true,
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSchemeClick = (scheme) => {
    setActiveScheme(scheme.scheme_code);
    setInputQuery(`Tell me the expense ratio and exit load for ${scheme.scheme_name}`);
    inputRef.current?.focus();
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-background text-on-surface font-body-sm overflow-hidden select-none">
      {/* 1. Top Compliance Banner */}
      <header className="w-full bg-surface-container-highest border-b border-tertiary/20 py-1.5 px-4 flex items-center justify-center gap-2 z-50 relative shrink-0">
        <span className="material-symbols-outlined text-tertiary text-[18px]">warning</span>
        <p className="font-body-sm text-tertiary text-center text-xs sm:text-sm">
          <strong>Regulatory Notice:</strong> Facts-only information sourced exclusively from verified Groww scheme factsheets. No investment advice, predictions, or return calculations provided.
        </p>
      </header>

      {/* 2. Glassmorphic Navbar */}
      <nav className="w-full glass-panel z-40 relative flex items-center justify-between px-4 sm:px-6 py-3 shrink-0 border-x-0 border-t-0 shadow-sm">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="font-headline-md text-xl sm:text-2xl text-primary font-bold tracking-tight flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-2xl">account_balance</span>
              Mutual Fund FAQ Assistant
            </h1>
            <p className="font-body-sm text-xs text-on-surface-variant">HDFC Schemes Knowledge Base • Facts-Only RAG</p>
          </div>

          {/* Scheme Filter Pills (Desktop) */}
          <div className="hidden xl:flex items-center gap-2 ml-6">
            <button
              onClick={() => setActiveScheme("all")}
              className={`px-3 py-1 rounded-full border text-xs font-semibold transition-all ${
                activeScheme === "all"
                  ? "border-primary/50 bg-primary/15 text-primary shadow-[0_0_12px_rgba(68,237,183,0.25)]"
                  : "border-outline-variant bg-surface-container-low text-on-surface-variant hover:bg-surface-variant hover:text-on-surface"
              }`}
            >
              All Schemes
            </button>
            {schemes.slice(0, 4).map((s) => (
              <button
                key={s.scheme_code}
                onClick={() => handleSchemeClick(s)}
                className={`px-3 py-1 rounded-full border text-xs font-semibold transition-all truncate max-w-[140px] ${
                  activeScheme === s.scheme_code
                    ? "border-primary/50 bg-primary/15 text-primary"
                    : "border-outline-variant bg-surface-container-low text-on-surface-variant hover:bg-surface-variant hover:text-on-surface"
                }`}
                title={s.scheme_name}
              >
                {s.scheme_name.replace("HDFC ", "")}
              </button>
            ))}
          </div>
        </div>

        {/* Status Badge & Mobile Sidebar Toggle */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-surface-container-highest px-3 py-1.5 rounded-lg border border-outline-variant">
            <div className="w-2.5 h-2.5 rounded-full bg-primary status-dot"></div>
            <span className="font-mono-data text-xs text-on-surface-variant">
              openai/gpt-oss-120b • {healthStatus.indexed} Chunks
            </span>
          </div>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="xl:hidden p-2 rounded-lg bg-surface-container-highest border border-outline-variant text-on-surface hover:text-primary transition-colors"
            title="Toggle Scheme Explorer"
          >
            <span className="material-symbols-outlined text-[20px]">explore</span>
          </button>
        </div>
      </nav>

      {/* 3. Main Body Layout (Chat Area + Sidebar) */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Central Chat Stream */}
        <main className="flex-1 flex flex-col relative h-full bg-surface-dim/40 border-r border-outline-variant z-10">
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-36 flex flex-col gap-6">
            {/* Starter Prompt Chips */}
            {messages.length <= 1 && (
              <div className="flex flex-col items-center justify-center pt-8 pb-4 gap-4 opacity-90 message-animate">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary shadow-[0_0_20px_rgba(68,237,183,0.2)]">
                  <span className="material-symbols-outlined text-2xl">quick_reference</span>
                </div>
                <h3 className="font-headline-md text-lg text-on-surface font-semibold">
                  Frequently Asked Mutual Fund Questions
                </h3>
                <div className="flex flex-wrap justify-center gap-2.5 max-w-2xl">
                  {STARTER_PROMPTS.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSubmit(prompt.label)}
                      className="glass-panel px-4 py-2.5 rounded-xl text-on-surface font-body-sm hover:bg-surface-variant hover:text-primary hover:border-primary/40 transition-all border border-outline-variant text-left flex items-center gap-2.5 group shadow-sm"
                    >
                      <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary text-[18px]">
                        {prompt.icon}
                      </span>
                      <span>{prompt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Message Stream */}
            <div className="flex flex-col gap-5 max-w-4xl mx-auto w-full">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex w-full message-animate ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.sender === "user" ? (
                    <div className="bg-surface-bright rounded-2xl rounded-tr-none px-5 py-3 border border-outline-variant max-w-[85%] sm:max-w-[75%] shadow-md select-text">
                      <p className="font-body-md text-on-surface leading-relaxed">{msg.text}</p>
                      {msg.timestamp && (
                        <p className="text-[10px] text-on-surface-variant text-right mt-1 font-mono-data">
                          {msg.timestamp}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="flex gap-3.5 max-w-[95%] sm:max-w-[90%] select-text">
                      {/* Assistant Avatar */}
                      <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/50 shadow-[0_0_12px_rgba(68,237,183,0.3)]">
                        <span className="material-symbols-outlined text-primary text-[18px]">robot_2</span>
                      </div>

                      <div className="flex flex-col gap-2.5 w-full">
                        {/* Status & Latency Badge Header */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {msg.status === "blocked" ? (
                              <span className="px-2.5 py-0.5 rounded-full bg-error-container/20 border border-error/50 text-error font-label-caps text-[10px] flex items-center gap-1">
                                <span className="material-symbols-outlined text-[12px]">security</span>
                                PII Blocked
                              </span>
                            ) : msg.status === "refusal" ? (
                              <span className="px-2.5 py-0.5 rounded-full bg-tertiary-container/20 border border-tertiary/50 text-tertiary font-label-caps text-[10px] flex items-center gap-1">
                                <span className="material-symbols-outlined text-[12px]">shield</span>
                                Non-Advisory Guardrail
                              </span>
                            ) : msg.status === "disambiguation" ? (
                              <span className="px-2.5 py-0.5 rounded-full bg-secondary-container/20 border border-secondary/50 text-secondary font-label-caps text-[10px] flex items-center gap-1">
                                <span className="material-symbols-outlined text-[12px]">help</span>
                                Scheme Disambiguation
                              </span>
                            ) : (
                              <span className="px-2.5 py-0.5 rounded-full bg-primary/15 border border-primary/40 text-primary font-label-caps text-[10px] flex items-center gap-1">
                                <span className="material-symbols-outlined text-[12px]">verified</span>
                                Verified Factual Response
                              </span>
                            )}

                            {msg.latency_ms > 0 && (
                              <span className="font-mono-data text-[11px] text-on-surface-variant flex items-center gap-0.5">
                                <span className="material-symbols-outlined text-[13px]">bolt</span>
                                {msg.latency_ms}ms
                              </span>
                            )}
                          </div>

                          <button
                            onClick={() => handleCopy(msg.id, msg.text)}
                            className="text-on-surface-variant hover:text-primary transition-colors p-1 rounded hover:bg-surface-variant text-xs flex items-center gap-1"
                            title="Copy response"
                          >
                            <span className="material-symbols-outlined text-[14px]">
                              {copiedId === msg.id ? "check" : "content_copy"}
                            </span>
                            <span className="text-[10px]">{copiedId === msg.id ? "Copied" : "Copy"}</span>
                          </button>
                        </div>

                        {/* Core Response Bubble */}
                        <div className="glass-panel rounded-2xl rounded-tl-none px-5 py-3.5 neon-glow">
                          <p className="font-body-md text-on-surface leading-relaxed whitespace-pre-line">
                            {msg.text}
                          </p>
                        </div>

                        {/* Citation Card */}
                        {msg.source_url && (
                          <a
                            href={msg.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="glass-panel p-3 rounded-xl flex items-center justify-between hover:bg-surface-variant hover:border-primary/40 transition-all group cursor-pointer max-w-md shadow-sm"
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-primary/15 rounded-lg flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined text-[16px]">description</span>
                              </div>
                              <div className="truncate">
                                <p className="font-title-sm text-xs text-on-surface group-hover:text-primary transition-colors">
                                  Source: Groww Verified Factsheet
                                </p>
                                <p className="font-mono-data text-[11px] text-on-surface-variant truncate">
                                  {msg.source_url}
                                </p>
                              </div>
                            </div>
                            <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors text-[18px] shrink-0 ml-2">
                              open_in_new
                            </span>
                          </a>
                        )}

                        {/* Compliance Footer */}
                        {msg.last_updated && (
                          <div className="flex items-center gap-2 text-[11px] text-on-surface-variant/70 font-mono-data pl-1">
                            <span>Last updated from sources: {msg.last_updated}</span>
                            <span>•</span>
                            <span>Facts-only. No investment advice.</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
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

          {/* 4. Bottom Floating Input Bar */}
          <div className="absolute bottom-0 left-0 w-full p-4 sm:p-6 bg-gradient-to-t from-background via-background/95 to-transparent z-20">
            <div className="max-w-4xl mx-auto flex flex-col gap-2">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSubmit();
                }}
                className="relative flex items-center group"
              >
                <input
                  ref={inputRef}
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  disabled={loading}
                  placeholder="Ask about exit loads, expense ratios (TER), minimum SIP limits, lock-in period..."
                  className="w-full bg-surface-container-low border border-outline-variant rounded-full py-3.5 sm:py-4 pl-5 sm:pl-6 pr-14 text-on-surface font-body-md placeholder:text-on-surface-variant/70 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-lg transition-all group-hover:border-outline text-sm sm:text-base disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={!inputQuery.trim() || loading}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center hover:bg-primary transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-[0_0_15px_rgba(0,208,156,0.4)]"
                  title="Send query"
                >
                  <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    send
                  </span>
                </button>
              </form>

              {/* Safety Micro-Hint */}
              <div className="flex items-center justify-center gap-1.5 text-on-surface-variant/80 font-body-sm text-xs text-center">
                <span className="material-symbols-outlined text-[14px] text-primary">lock</span>
                <span>Zero PII Storage • Do not enter PAN, Aadhaar, OTPs, or bank account credentials.</span>
              </div>
            </div>
          </div>
        </main>

        {/* 5. Right Sidebar: Scheme Explorer */}
        <aside
          className={`fixed xl:static right-0 top-0 h-full w-80 bg-surface flex flex-col border-l border-outline-variant shrink-0 z-30 transition-transform duration-300 ${
            sidebarOpen ? "translate-x-0" : "translate-x-full xl:translate-x-0"
          }`}
        >
          <div className="p-4 border-b border-outline-variant bg-surface-container-highest flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">explore</span>
              <h2 className="font-title-sm text-sm font-bold text-on-surface">Curated Scheme Explorer</h2>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="xl:hidden text-on-surface-variant hover:text-on-surface"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
            {schemes.map((scheme) => (
              <div
                key={scheme.scheme_code}
                onClick={() => handleSchemeClick(scheme)}
                className={`glass-panel p-4 rounded-xl flex flex-col gap-2.5 transition-all cursor-pointer group hover:border-primary/60 hover:shadow-[0_0_15px_rgba(68,237,183,0.15)] ${
                  activeScheme === scheme.scheme_code
                    ? "border-t-[3px] border-t-primary bg-surface-container-highest"
                    : ""
                }`}
              >
                <div className="flex justify-between items-start gap-2">
                  <h3 className="font-title-sm text-xs font-semibold text-on-surface group-hover:text-primary transition-colors leading-tight">
                    {scheme.scheme_name}
                  </h3>
                  <span
                    className={`px-2 py-0.5 rounded-md font-label-caps text-[9px] border whitespace-nowrap ${
                      (scheme.riskometer || "").toLowerCase().includes("very high")
                        ? "bg-error/10 text-error border-error/25"
                        : "bg-tertiary-container/20 text-tertiary border-tertiary-container/30"
                    }`}
                  >
                    {scheme.riskometer || "High Risk"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex flex-col">
                    <span className="font-label-caps text-on-surface-variant text-[9px]">CATEGORY</span>
                    <span className="font-body-sm text-on-surface text-[11px] truncate">{scheme.category}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-label-caps text-on-surface-variant text-[9px]">DIRECT TER</span>
                    <span className="font-mono-data text-primary text-[11px] font-bold">
                      {scheme.ter || "View"}
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-outline-variant/40 flex items-center justify-between">
                  <div className="truncate max-w-[170px]">
                    <span className="font-label-caps text-on-surface-variant text-[9px] block">BENCHMARK</span>
                    <p className="font-body-sm text-on-surface text-[10px] truncate">{scheme.benchmark_index}</p>
                  </div>
                  <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary text-[16px]">
                    chevron_right
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Telemetry Footer */}
          <div className="p-3 border-t border-outline-variant bg-surface-container-lowest text-center">
            <p className="text-[10px] text-on-surface-variant font-mono-data">
              Groq LPU Quota: 30 RPM • 8K TPM • 1K RPD
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

// Render root component
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
