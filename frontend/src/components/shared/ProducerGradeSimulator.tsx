import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Sparkles, Sliders, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface DefectItem {
  id: string;
  label: string;
  category: string;
  complaint_percentage: number;
  negative_mentions_count?: number;
  severity: 'critical' | 'high' | 'moderate';
  evidence_snippets: string[];
  potential_rating_gain: number;
  projected_rating_if_fixed: number;
  projected_grade_if_fixed: string;
}

export interface ProducerGradeSimulatorProps {
  productName: string;
  baseRating: number;
  defects?: DefectItem[];
  bottleneckSummary?: string;
  className?: string;
}

export function ProducerGradeSimulator({
  productName,
  baseRating = 3.4,
  defects = [],
  bottleneckSummary,
  className,
}: ProducerGradeSimulatorProps) {
  // Fallback defaults if no defects provided
  const activeDefects: DefectItem[] = defects.length > 0 ? defects : [
    {
      id: 'battery_power',
      label: 'Battery Degradation & Case Charging Failure',
      category: 'hardware',
      complaint_percentage: 58.0,
      negative_mentions_count: 14,
      severity: 'critical',
      evidence_snippets: [
        'Left earbud drains in 35 mins while right earbud lasts 3 hours.',
        'Charging case pins fail to make contact after 45 days.'
      ],
      potential_rating_gain: 0.8,
      projected_rating_if_fixed: 4.2,
      projected_grade_if_fixed: 'A'
    },
    {
      id: 'logistics_delivery',
      label: 'Courier & 2-Day Prime Transit Delays',
      category: 'logistics',
      complaint_percentage: 24.0,
      negative_mentions_count: 6,
      severity: 'high',
      evidence_snippets: [
        'Amazon promised 2-day delivery, took 6 days with outer packaging crushed.'
      ],
      potential_rating_gain: 0.3,
      projected_rating_if_fixed: 3.7,
      projected_grade_if_fixed: 'B'
    },
    {
      id: 'audio_sound',
      label: 'Microphone Wind Distortion During Calls',
      category: 'audio',
      complaint_percentage: 18.0,
      negative_mentions_count: 4,
      severity: 'moderate',
      evidence_snippets: [
        'Opposite person hears massive static echo when outdoors.'
      ],
      potential_rating_gain: 0.2,
      projected_rating_if_fixed: 3.6,
      projected_grade_if_fixed: 'B'
    }
  ];

  // Track which fixes are toggled
  const [fixedIds, setFixedIds] = useState<Record<string, boolean>>({});

  const toggleFix = (id: string) => {
    setFixedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // Calculate simulated rating
  const totalGain = activeDefects.reduce((acc, d) => {
    return fixedIds[d.id] ? acc + d.potential_rating_gain : acc;
  }, 0);

  const simulatedRating = Math.min(+(baseRating + totalGain).toFixed(1), 5.0);

  const getGrade = (r: number) => {
    if (r >= 4.5) return { grade: 'Grade A+', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
    if (r >= 4.0) return { grade: 'Grade A', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
    if (r >= 3.5) return { grade: 'Grade B', color: 'text-blue-400 bg-blue-500/10 border-blue-500/30' };
    if (r >= 3.0) return { grade: 'Grade C', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' };
    return { grade: 'Grade D', color: 'text-rose-400 bg-rose-500/10 border-rose-500/30' };
  };

  const baseGrade = getGrade(baseRating);
  const currentSimGrade = getGrade(simulatedRating);

  return (
    <Card className={cn('relative overflow-hidden border border-white/10 bg-slate-950/80 p-6 backdrop-blur-xl', className)}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-rp-primary/20 text-rp-primary">
              <Sliders className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-white">
              Producer & Brand Quality Simulator
            </h3>
            <Badge tone="neutral" className="border-purple-500/30 bg-purple-500/10 text-xs text-purple-300">
              Live n8n Intelligence
            </Badge>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            {bottleneckSummary || `Identifies why ${productName} ratings are dropping on Amazon/Flipkart and simulates projected grade post-fix.`}
          </p>
        </div>

        {/* Live Scorecard Preview */}
        <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/90 px-4 py-2.5">
          <div className="text-right">
            <div className="text-[11px] font-medium text-slate-400">Current Rating</div>
            <div className="flex items-center justify-end gap-1.5">
              <span className="text-lg font-bold text-white">{baseRating.toFixed(1)} ⭐</span>
              <span className={cn('rounded px-1.5 py-0.5 text-[10px] font-bold border', baseGrade.color)}>
                {baseGrade.grade}
              </span>
            </div>
          </div>

          <div className="text-slate-600">→</div>

          <div className="text-left">
            <div className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
              <span>Simulated Post-Fix</span>
              {totalGain > 0 && <span className="font-bold text-emerald-400">(+{totalGain.toFixed(1)})</span>}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-lg font-bold text-emerald-300">{simulatedRating.toFixed(1)} ⭐</span>
              <span className={cn('rounded px-1.5 py-0.5 text-[10px] font-bold border', currentSimGrade.color)}>
                {currentSimGrade.grade}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Defect Toggles & Evidence Grid */}
      <div className="mt-5 space-y-3">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Root Causes Identified from Scraped Reviews (Toggle Fix to Simulate Gain)
        </div>

        <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {activeDefects.map((defect) => {
            const isChecked = !!fixedIds[defect.id];

            return (
              <div
                key={defect.id}
                onClick={() => toggleFix(defect.id)}
                className={cn(
                  'cursor-pointer rounded-xl border p-4 transition-all duration-200 select-none',
                  isChecked
                    ? 'border-emerald-500/50 bg-emerald-500/10 shadow-lg shadow-emerald-500/5'
                    : 'border-white/10 bg-slate-900/60 hover:border-white/20 hover:bg-slate-900/80'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => {}} // handled by parent div
                      className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-emerald-500 focus:ring-emerald-500"
                    />
                    <span className="text-xs font-semibold text-white">
                      {defect.label}
                    </span>
                  </div>
                  <span
                    className={cn(
                      'rounded px-1.5 py-0.5 text-[10px] font-bold uppercase',
                      defect.severity === 'critical'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : defect.severity === 'high'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    )}
                  >
                    {defect.complaint_percentage}% of complaints
                  </span>
                </div>

                {/* Evidence quotes */}
                {defect.evidence_snippets && defect.evidence_snippets.length > 0 && (
                  <div className="mt-2.5 rounded-lg bg-black/40 p-2 text-[11px] italic text-slate-400">
                    "{defect.evidence_snippets[0]}"
                  </div>
                )}

                {/* Impact delta */}
                <div className="mt-3 flex items-center justify-between text-xs border-t border-white/5 pt-2">
                  <span className="text-slate-400">Fixing unlocks:</span>
                  <span className="font-semibold text-emerald-400 flex items-center gap-0.5">
                    <TrendingUp className="h-3 w-3" />
                    +{defect.potential_rating_gain.toFixed(1)} Stars → {defect.projected_grade_if_fixed}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Simulator Footer Action */}
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-900/40 p-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-400" />
          <span>
            {totalGain > 0
              ? `Simulating ${Object.values(fixedIds).filter(Boolean).length} fixes: Product projected to reach ${simulatedRating} ⭐ (${currentSimGrade.grade})!`
              : 'Click any defect card above to simulate how factory QA or logistics improvements improve your public catalog grade.'}
          </span>
        </div>
        {totalGain > 0 && (
          <button
            onClick={() => setFixedIds({})}
            className="text-[11px] font-semibold text-slate-400 underline hover:text-white"
          >
            Reset Simulator
          </button>
        )}
      </div>
    </Card>
  );
}
