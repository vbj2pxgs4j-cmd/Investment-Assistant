import React from 'react';

const STARTER_PROMPTS = [
  {
    icon: 'bar_chart',
    label: 'What is the exit load for HDFC Small Cap Fund?',
    scheme: 'hdfc-small-cap-fund-direct-growth',
  },
  {
    icon: 'lock',
    label: 'What is the lock-in period for HDFC ELSS Tax Saver Fund?',
    scheme: 'hdfc-elss-tax-saver-fund-direct-plan-growth',
  },
  {
    icon: 'payments',
    label: 'What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?',
    scheme: 'hdfc-mid-cap-fund-direct-growth',
  },
  {
    icon: 'percent',
    label: 'What is the Total Expense Ratio (TER) of HDFC Top 100 Fund?',
    scheme: 'hdfc-large-cap-fund-direct-growth',
  },
  {
    icon: 'description',
    label: 'How do I download my mutual fund capital gains statement?',
    scheme: null,
  },
];

export default function StarterChips({ onSelectPrompt }) {
  return (
    <div className="flex flex-col items-center justify-center pt-8 pb-4 gap-4 opacity-90 message-animate">
      <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary shadow-[0_0_20px_rgba(68,237,183,0.2)]">
        <span className="material-symbols-outlined text-2xl">quick_reference</span>
      </div>
      <h3 className="font-headline-md text-lg text-on-surface font-semibold text-center">
        Frequently Asked Mutual Fund Questions
      </h3>
      <div className="flex flex-wrap justify-center gap-2.5 max-w-2xl">
        {STARTER_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(prompt.label)}
            className="glass-panel px-4 py-2.5 rounded-xl text-on-surface font-body-sm hover:bg-surface-variant hover:text-primary hover:border-primary/40 transition-all border border-outline-variant text-left flex items-center gap-2.5 group shadow-sm cursor-pointer"
          >
            <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary text-[18px]">
              {prompt.icon}
            </span>
            <span>{prompt.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
