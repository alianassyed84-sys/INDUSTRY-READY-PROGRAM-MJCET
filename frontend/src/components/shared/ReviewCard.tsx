import { useState } from 'react';
import { Star } from 'lucide-react';
import { Badge, type BadgeTone } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { fmtDate } from '@/lib/utils';
import type { Review } from '@/lib/types';

const tone: Record<string, BadgeTone> = { positive: 'success', neutral: 'neutral', negative: 'danger' };

/** Renders review text as plain text (never as HTML). Only fields that exist are shown. */
export function ReviewCard({ review }: { review: Review }) {
  const [open, setOpen] = useState(false);
  const long = review.text.length > 220;
  return (
    <Card interactive className="!p-5">
      <div className="mb-2.5 flex flex-wrap items-center gap-2">
        {review.rating != null && (
          <span className="tnum inline-flex items-center gap-1 text-sm font-bold" aria-label={`${review.rating} out of 5 stars`}>
            <Star className="h-4 w-4 fill-rp-warning text-rp-warning" aria-hidden />{review.rating}
          </span>
        )}
        {review.sentiment && <Badge tone={tone[review.sentiment]}>{review.sentiment}</Badge>}
        {review.language && <Badge tone="info">{review.language.toUpperCase()}</Badge>}
        {review.date && <time dateTime={review.date} className="ml-auto text-xs text-rp-muted">{fmtDate(review.date)}</time>}
      </div>
      <p className={`whitespace-pre-line break-words text-[15px] leading-relaxed ${!open && long ? 'line-clamp-3' : ''}`}>{review.text}</p>
      {long && <button onClick={() => setOpen((o) => !o)} className="mt-1.5 rounded text-sm font-semibold text-rp-primary hover:text-rp-primary-hover">{open ? 'Show less' : 'Read more'}</button>}
      {review.source && <p className="mt-3 text-xs text-rp-muted">Source: {review.source}</p>}
    </Card>
  );
}
