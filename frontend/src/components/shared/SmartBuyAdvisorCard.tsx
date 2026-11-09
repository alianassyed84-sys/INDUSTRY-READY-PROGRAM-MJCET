import { Card } from '@/components/ui/Card';
import { ShieldCheck, AlertOctagon, Clock, ThumbsUp, ThumbsDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SmartBuyAdvisorProps {
  verdict?: 'BUY_NOW' | 'WAIT_FOR_DROP' | 'AVOID_DEFECT';
  dealScore?: number;
  verdictReason?: string;
  honestPros?: string[];
  honestCons?: string[];
  criticalWarning?: string | null;
  bestSuitedFor?: string | null;
  notRecommendedFor?: string | null;
  className?: string;
}

export function SmartBuyAdvisorCard({
  verdict = 'AVOID_DEFECT',
  dealScore = 52,
  verdictReason = 'Multiple verified reviews report battery degradation within 60 days of purchase.',
  honestPros = [
    'Deep bass signature and loud max volume',
    'Comfortable lightweight fit for daily commutes',
    'USB Type-C quick charging support'
  ],
  honestCons = [
    'Battery capacity deteriorates noticeably after 2-3 months',
    'Microphone picks up heavy wind and road noise during outdoor calls'
  ],
  criticalWarning = 'Critical Defect Alert: 58% of negative reviews highlight left earbud charging failures.',
  bestSuitedFor = 'Budget-conscious listeners who prioritize sound over long battery life',
  notRecommendedFor = 'Heavy phone-callers or travelers needing 6+ hours of uninterrupted endurance',
  className,
}: SmartBuyAdvisorProps) {
  const getVerdictConfig = () => {
    switch (verdict) {
      case 'BUY_NOW':
        return {
          title: 'BUY NOW — RECOMMENDED DEAL',
          color: 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30',
          icon: ShieldCheck,
          scoreColor: 'text-emerald-400',
          barColor: 'bg-emerald-500',
        };
      case 'WAIT_FOR_DROP':
        return {
          title: 'WAIT — PRICE MAY DROP SOON',
          color: 'text-amber-400 bg-amber-500/15 border-amber-500/30',
          icon: Clock,
          scoreColor: 'text-amber-400',
          barColor: 'bg-amber-500',
        };
      case 'AVOID_DEFECT':
      default:
        return {
          title: 'CAUTION — KNOWN HARDWARE DEFECT',
          color: 'text-rose-400 bg-rose-500/15 border-rose-500/30',
          icon: AlertOctagon,
          scoreColor: 'text-rose-400',
          barColor: 'bg-rose-500',
        };
    }
  };

  const config = getVerdictConfig();
  const Icon = config.icon;

  return (
    <Card className={cn('relative overflow-hidden border border-white/10 bg-slate-950/80 p-6 backdrop-blur-xl', className)}>
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border', config.color)}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                BuyHatke-Style Smart Shopper Verdict
              </span>
              <span className="rounded bg-sky-500/10 px-2 py-0.5 text-[10px] font-semibold text-sky-400 border border-sky-500/20">
                Consumer AI
              </span>
            </div>
            <div className="mt-0.5 text-base font-bold text-white">
              {config.title}
            </div>
          </div>
        </div>

        {/* Deal Score Meter */}
        <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/90 px-4 py-2">
          <div className="text-right">
            <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Shopper Confidence Score</div>
            <div className="flex items-center justify-end gap-1">
              <span className={cn('text-2xl font-black', config.scoreColor)}>{dealScore}</span>
              <span className="text-xs text-slate-500 font-semibold">/100</span>
            </div>
          </div>
          <div className="h-8 w-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className={cn('w-full rounded-full transition-all duration-500', config.barColor)}
              style={{ height: `${dealScore}%` }}
            />
          </div>
        </div>
      </div>

      {/* Critical Defect Banner */}
      {criticalWarning && (
        <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-200">
          <AlertOctagon className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="font-medium">
            {criticalWarning}
          </div>
        </div>
      )}

      {/* Honest Verdict Reason */}
      <div className="mt-4 text-xs leading-relaxed text-slate-300">
        <span className="font-semibold text-white">Shopping Assistant Verdict: </span>
        {verdictReason}
      </div>

      {/* Pros & Cons Columns */}
      <div className="mt-5 grid gap-4 sm:grid-cols-1 md:grid-cols-2">
        {/* Pros */}
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2.5">
            <ThumbsUp className="h-3.5 w-3.5" />
            <span>Honest Verified Pros</span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-300">
            {honestPros.map((pro, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{pro}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Cons */}
        <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4">
          <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase tracking-wider mb-2.5">
            <ThumbsDown className="h-3.5 w-3.5" />
            <span>Known Compromises & Cons</span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-300">
            {honestCons.map((con, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-rose-400 font-bold">•</span>
                <span>{con}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Fit Profile */}
      <div className="mt-4 grid gap-3 text-xs sm:grid-cols-1 md:grid-cols-2 border-t border-white/5 pt-3">
        {bestSuitedFor && (
          <div className="text-slate-400">
            <span className="font-semibold text-emerald-300">Best for: </span>
            {bestSuitedFor}
          </div>
        )}
        {notRecommendedFor && (
          <div className="text-slate-400">
            <span className="font-semibold text-rose-300">Skip if: </span>
            {notRecommendedFor}
          </div>
        )}
      </div>
    </Card>
  );
}
