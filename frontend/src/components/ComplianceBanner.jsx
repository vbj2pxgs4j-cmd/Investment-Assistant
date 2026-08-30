import React from 'react';

export default function ComplianceBanner() {
  return (
    <header className="w-full bg-surface-container-highest border-b border-tertiary/20 py-1.5 px-4 flex items-center justify-center gap-2 z-50 relative shrink-0">
      <span className="material-symbols-outlined text-tertiary text-[18px]">warning</span>
      <p className="font-body-sm text-tertiary text-center text-xs sm:text-sm">
        <strong>Regulatory Notice:</strong> Facts-only information sourced exclusively from verified Groww scheme factsheets. No investment advice, predictions, or return calculations provided.
      </p>
    </header>
  );
}
