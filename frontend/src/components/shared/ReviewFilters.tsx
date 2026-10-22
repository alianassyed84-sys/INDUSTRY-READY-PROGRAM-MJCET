import { Search } from 'lucide-react';
import { Input } from '@/components/ui/Input';

export interface FilterState { q: string; rating: string; language: string; sentiment: string; sort: string }
export const EMPTY_FILTERS: FilterState = { q: '', rating: '', language: '', sentiment: '', sort: 'newest' };

interface Props {
  value: FilterState;
  onChange: (v: FilterState) => void;
  /** Filters render only when the corresponding field exists in the data. */
  available: { rating: boolean; language: boolean; sentiment: boolean; date: boolean };
  languages: string[];
}

const sel = 'min-h-[48px] w-full rounded-btn border border-rp-border bg-rp-surface px-3.5 text-sm font-medium focus:border-rp-primary';

export function ReviewFilters({ value, onChange, available, languages }: Props) {
  const set = (patch: Partial<FilterState>) => onChange({ ...value, ...patch });
  return (
    <div data-reveal className="grid gap-3 md:grid-cols-2 xl:grid-cols-[2fr_1fr_1fr_1fr_1fr]">
      <Input aria-label="Search within reviews" placeholder="Search within reviews" leading={<Search className="h-4 w-4" />} value={value.q} onChange={(e) => set({ q: e.target.value })} />
      {available.rating && (
        <select aria-label="Filter by rating" className={sel} value={value.rating} onChange={(e) => set({ rating: e.target.value })}>
          <option value="">All ratings</option>
          {[5, 4, 3, 2, 1].map((r) => <option key={r} value={r}>{r} stars</option>)}
        </select>
      )}
      {available.language && (
        <select aria-label="Filter by language" className={sel} value={value.language} onChange={(e) => set({ language: e.target.value })}>
          <option value="">All languages</option>
          {languages.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
        </select>
      )}
      {available.sentiment && (
        <select aria-label="Filter by sentiment" className={sel} value={value.sentiment} onChange={(e) => set({ sentiment: e.target.value })}>
          <option value="">All sentiment</option>
          <option value="positive">Positive</option><option value="neutral">Neutral</option><option value="negative">Negative</option>
        </select>
      )}
      <select aria-label="Sort reviews" className={sel} value={value.sort} onChange={(e) => set({ sort: e.target.value })}>
        {available.date && <><option value="newest">Newest first</option><option value="oldest">Oldest first</option></>}
        {available.rating && <><option value="high">Highest rating</option><option value="low">Lowest rating</option></>}
        {!available.date && !available.rating && <option value="newest">Default order</option>}
      </select>
    </div>
  );
}
