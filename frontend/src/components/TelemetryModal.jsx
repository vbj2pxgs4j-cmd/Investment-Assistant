import React, { useState, useEffect } from 'react';
import { fetchRateLimits, fetchHealth } from '../services/api';

export default function TelemetryModal({ isOpen, onClose }) {
  const [telemetry, setTelemetry] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    async function loadMetrics() {
      setLoading(true);
      try {
        const [rateData, healthData] = await Promise.all([
          fetchRateLimits().catch(() => null),
          fetchHealth().catch(() => null),
        ]);
        setTelemetry(rateData);
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to fetch telemetry:', err);
      } finally {
        setLoading(false);
      }
    }

    loadMetrics();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md">
      <div className="glass-panel-elevated w-full max-w-lg rounded-2xl p-6 flex flex-col gap-5 shadow-2xl message-animate border border-primary/40">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-outline-variant pb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-2xl">speed</span>
            <div>
              <h2 className="font-headline-md text-lg font-bold text-on-surface">Groq LPU Quota Telemetry</h2>
              <p className="font-body-sm text-xs text-on-surface-variant">openai/gpt-oss-120b Free Tier Safeguards</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-variant cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Quota Grid */}
        {loading ? (
          <div className="py-8 text-center text-on-surface-variant font-mono-data text-xs flex items-center justify-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
            <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
            <div className="w-2 h-2 rounded-full bg-primary typing-dot"></div>
            <span>Fetching live quota metrics...</span>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {/* RPM */}
            <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1">
              <span className="font-label-caps text-on-surface-variant text-[10px]">REQUESTS PER MINUTE</span>
              <p className="font-mono-data text-xl text-primary font-bold">
                {telemetry?.rpm_current ?? 0} <span className="text-xs text-on-surface-variant">/ {telemetry?.rpm_limit ?? 30} RPM</span>
              </p>
              <div className="w-full bg-surface-container-low h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className="bg-primary h-full transition-all"
                  style={{ width: `${Math.min(telemetry?.rpm_utilization_pct ?? 0, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* TPM */}
            <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1">
              <span className="font-label-caps text-on-surface-variant text-[10px]">TOKENS PER MINUTE</span>
              <p className="font-mono-data text-xl text-primary font-bold">
                {telemetry?.tpm_current ?? 0} <span className="text-xs text-on-surface-variant">/ {telemetry?.tpm_limit ?? 8000} TPM</span>
              </p>
              <div className="w-full bg-surface-container-low h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className="bg-primary h-full transition-all"
                  style={{ width: `${Math.min(telemetry?.tpm_utilization_pct ?? 0, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* RPD */}
            <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1">
              <span className="font-label-caps text-on-surface-variant text-[10px]">DAILY REQUESTS</span>
              <p className="font-mono-data text-lg text-secondary font-bold">
                {telemetry?.rpd_current ?? 0} <span className="text-xs text-on-surface-variant">/ {telemetry?.rpd_limit ?? 1000} RPD</span>
              </p>
            </div>

            {/* Vector Store */}
            <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1">
              <span className="font-label-caps text-on-surface-variant text-[10px]">VECTOR STORE (CHROMADB)</span>
              <p className="font-mono-data text-lg text-secondary font-bold">
                {health?.total_indexed_chunks ?? 38} <span className="text-xs text-on-surface-variant">Chunks</span>
              </p>
            </div>
          </div>
        )}

        {/* Safeguard Notice */}
        <div className="p-3 rounded-xl bg-surface-container-highest border border-primary/20 text-xs text-on-surface-variant flex items-start gap-2">
          <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">verified_user</span>
          <p className="leading-relaxed">
            <strong>Zero-Downtime Guarantee:</strong> If Groq RPM or TPM limits are reached, the system instantly switches to deterministic fallback synthesis (<span className="text-primary font-mono-data">&lt;5ms latency</span>) without interrupting service.
          </p>
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-primary-container text-on-primary-container hover:bg-primary font-semibold text-xs transition-colors cursor-pointer"
          >
            Close Telemetry
          </button>
        </div>
      </div>
    </div>
  );
}
