import React, { useState } from 'react';

export default function ChatMessage({ message }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (message.sender === 'user') {
    return (
      <div className="flex w-full justify-end message-animate">
        <div className="bg-surface-bright rounded-2xl rounded-tr-none px-5 py-3 border border-outline-variant max-w-[85%] sm:max-w-[75%] shadow-md select-text">
          <p className="font-body-md text-on-surface leading-relaxed">{message.text}</p>
          {message.timestamp && (
            <p className="text-[10px] text-on-surface-variant text-right mt-1 font-mono-data">
              {message.timestamp}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full justify-start message-animate select-text">
      <div className="flex gap-3.5 max-w-[95%] sm:max-w-[90%]">
        {/* Assistant Avatar */}
        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/50 shadow-[0_0_12px_rgba(68,237,183,0.3)]">
          <span className="material-symbols-outlined text-primary text-[18px]">robot_2</span>
        </div>

        <div className="flex flex-col gap-2.5 w-full">
          {/* Status & Latency Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 flex-wrap">
              {message.status === 'blocked' ? (
                <span className="px-2.5 py-0.5 rounded-full bg-error-container/20 border border-error/50 text-error font-label-caps text-[10px] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">security</span>
                  PII Blocked
                </span>
              ) : message.status === 'refusal' ? (
                <span className="px-2.5 py-0.5 rounded-full bg-tertiary-container/20 border border-tertiary/50 text-tertiary font-label-caps text-[10px] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">shield</span>
                  Non-Advisory Guardrail
                </span>
              ) : message.status === 'disambiguation' ? (
                <span className="px-2.5 py-0.5 rounded-full bg-secondary-container/20 border border-secondary/50 text-secondary font-label-caps text-[10px] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">help</span>
                  Scheme Disambiguation
                </span>
              ) : message.status === 'error' ? (
                <span className="px-2.5 py-0.5 rounded-full bg-error/15 border border-error/40 text-error font-label-caps text-[10px] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">error</span>
                  Connection Notice
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded-full bg-primary/15 border border-primary/40 text-primary font-label-caps text-[10px] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">verified</span>
                  Verified Factual Response
                </span>
              )}

              {message.latency_ms > 0 && (
                <span className="font-mono-data text-[11px] text-on-surface-variant flex items-center gap-0.5">
                  <span className="material-symbols-outlined text-[13px]">bolt</span>
                  {message.latency_ms}ms
                </span>
              )}

              {message.is_fallback && (
                <span className="font-mono-data text-[10px] text-on-surface-variant/70 border border-outline-variant px-1.5 py-0.5 rounded">
                  deterministic-fallback
                </span>
              )}
            </div>

            <button
              onClick={handleCopy}
              className="text-on-surface-variant hover:text-primary transition-colors p-1 rounded hover:bg-surface-variant text-xs flex items-center gap-1 cursor-pointer"
              title="Copy response"
            >
              <span className="material-symbols-outlined text-[14px]">
                {copied ? 'check' : 'content_copy'}
              </span>
              <span className="text-[10px]">{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          {/* Core Response Bubble */}
          <div className="glass-panel rounded-2xl rounded-tl-none px-5 py-3.5 neon-glow">
            <p className="font-body-md text-on-surface leading-relaxed whitespace-pre-line">
              {message.text}
            </p>
          </div>

          {/* Citation Card */}
          {message.source_url && (
            <a
              href={message.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="glass-panel p-3 rounded-xl flex items-center justify-between hover:bg-surface-variant hover:border-primary/40 transition-all group cursor-pointer max-w-md shadow-sm"
            >
              <div className="flex items-center gap-3 truncate">
                <div className="w-8 h-8 bg-primary/15 rounded-lg flex items-center justify-center text-primary shrink-0">
                  <span className="material-symbols-outlined text-[16px]">description</span>
                </div>
                <div className="truncate">
                  <p className="font-title-sm text-xs text-on-surface group-hover:text-primary transition-colors">
                    Source: Groww Verified Factsheet
                  </p>
                  <p className="font-mono-data text-[11px] text-on-surface-variant truncate">
                    {message.source_url}
                  </p>
                </div>
              </div>
              <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors text-[18px] shrink-0 ml-2">
                open_in_new
              </span>
            </a>
          )}

          {/* Compliance Footer */}
          {message.last_updated && (
            <div className="flex items-center gap-2 text-[11px] text-on-surface-variant/70 font-mono-data pl-1">
              <span>Last updated from sources: {message.last_updated}</span>
              <span>•</span>
              <span>Facts-only. No investment advice.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
