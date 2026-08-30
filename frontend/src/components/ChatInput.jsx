import React, { useRef, useEffect } from 'react';

export default function ChatInput({ inputQuery, setInputQuery, onSubmit, loading }) {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || loading) return;
    onSubmit();
  };

  return (
    <div className="absolute bottom-0 left-0 w-full p-4 sm:p-6 bg-gradient-to-t from-background via-background/95 to-transparent z-20">
      <div className="max-w-4xl mx-auto flex flex-col gap-2">
        <form onSubmit={handleFormSubmit} className="relative flex items-center group">
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
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center hover:bg-primary transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-[0_0_15px_rgba(0,208,156,0.4)] cursor-pointer"
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
  );
}
