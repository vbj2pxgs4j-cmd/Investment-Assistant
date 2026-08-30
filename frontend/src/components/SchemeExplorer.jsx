import React from 'react';

export default function SchemeExplorer({
  schemes,
  activeScheme,
  onSchemeClick,
  isOpen,
  onClose,
}) {
  return (
    <aside
      className={`fixed xl:static right-0 top-0 h-full w-80 bg-surface flex flex-col border-l border-outline-variant shrink-0 z-30 transition-transform duration-300 ${
        isOpen ? 'translate-x-0' : 'translate-x-full xl:translate-x-0'
      }`}
    >
      <div className="p-4 border-b border-outline-variant bg-surface-container-highest flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[20px]">explore</span>
          <h2 className="font-title-sm text-sm font-bold text-on-surface">Curated Scheme Explorer</h2>
        </div>
        <button
          onClick={onClose}
          className="xl:hidden text-on-surface-variant hover:text-on-surface p-1 rounded hover:bg-surface-variant cursor-pointer"
        >
          <span className="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {schemes.map((scheme) => (
          <div
            key={scheme.scheme_code}
            onClick={() => onSchemeClick(scheme)}
            className={`glass-panel p-4 rounded-xl flex flex-col gap-2.5 transition-all cursor-pointer group hover:border-primary/60 hover:shadow-[0_0_15px_rgba(68,237,183,0.15)] ${
              activeScheme === scheme.scheme_code
                ? 'border-t-[3px] border-t-primary bg-surface-container-highest'
                : ''
            }`}
          >
            <div className="flex justify-between items-start gap-2">
              <h3 className="font-title-sm text-xs font-semibold text-on-surface group-hover:text-primary transition-colors leading-tight">
                {scheme.scheme_name}
              </h3>
              <span
                className={`px-2 py-0.5 rounded-md font-label-caps text-[9px] border whitespace-nowrap ${
                  (scheme.riskometer || '').toLowerCase().includes('very high')
                    ? 'bg-error/10 text-error border-error/25'
                    : 'bg-tertiary-container/20 text-tertiary border-tertiary-container/30'
                }`}
              >
                {scheme.riskometer || 'High Risk'}
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
                  {scheme.ter || '0.74%'}
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
  );
}
