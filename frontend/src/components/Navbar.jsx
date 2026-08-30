import React from 'react';

export default function Navbar({
  schemes,
  activeScheme,
  onSchemeSelect,
  onToggleSidebar,
  healthStatus,
  onOpenTelemetry,
}) {
  return (
    <nav className="w-full glass-panel z-40 relative flex items-center justify-between px-4 sm:px-6 py-3 shrink-0 border-x-0 border-t-0 shadow-sm">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="font-headline-md text-xl sm:text-2xl text-primary font-bold tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-2xl">account_balance</span>
            Mutual Fund FAQ Assistant
          </h1>
          <p className="font-body-sm text-xs text-on-surface-variant">
            HDFC Schemes Knowledge Base • Facts-Only RAG
          </p>
        </div>

        {/* Scheme Filter Pills (Desktop) */}
        <div className="hidden xl:flex items-center gap-2 ml-6">
          <button
            onClick={() => onSchemeSelect('all')}
            className={`px-3 py-1 rounded-full border text-xs font-semibold transition-all ${
              activeScheme === 'all'
                ? 'border-primary/50 bg-primary/15 text-primary shadow-[0_0_12px_rgba(68,237,183,0.25)]'
                : 'border-outline-variant bg-surface-container-low text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`}
          >
            All Schemes
          </button>
          {schemes.slice(0, 4).map((s) => (
            <button
              key={s.scheme_code}
              onClick={() => onSchemeSelect(s.scheme_code, s.scheme_name)}
              className={`px-3 py-1 rounded-full border text-xs font-semibold transition-all truncate max-w-[140px] ${
                activeScheme === s.scheme_code
                  ? 'border-primary/50 bg-primary/15 text-primary'
                  : 'border-outline-variant bg-surface-container-low text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
              }`}
              title={s.scheme_name}
            >
              {s.scheme_name.replace('HDFC ', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Status Badge & Quota Metrics */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenTelemetry}
          className="hidden sm:flex items-center gap-2 bg-surface-container-highest hover:bg-surface-variant px-3 py-1.5 rounded-lg border border-outline-variant transition-colors group cursor-pointer"
          title="View Groq Quota & Model Telemetry"
        >
          <div className="w-2.5 h-2.5 rounded-full bg-primary status-dot"></div>
          <span className="font-mono-data text-xs text-on-surface-variant group-hover:text-on-surface">
            openai/gpt-oss-120b • {healthStatus.indexed} Chunks
          </span>
          <span className="material-symbols-outlined text-[14px] text-on-surface-variant group-hover:text-primary">
            speed
          </span>
        </button>

        <button
          onClick={onToggleSidebar}
          className="xl:hidden p-2 rounded-lg bg-surface-container-highest border border-outline-variant text-on-surface hover:text-primary transition-colors"
          title="Toggle Scheme Explorer"
        >
          <span className="material-symbols-outlined text-[20px]">explore</span>
        </button>
      </div>
    </nav>
  );
}
