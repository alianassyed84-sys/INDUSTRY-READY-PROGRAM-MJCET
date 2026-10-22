import { useEffect, useRef, type ReactNode } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

export function Dialog({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);
  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && onClose()}
      aria-labelledby="dialog-title"
      className="w-[min(92vw,480px)] rounded-card border border-rp-border bg-rp-surface p-0 shadow-lift backdrop:bg-rp-navy/40 backdrop:backdrop-blur-sm"
    >
      <div className="p-6">
        <div className="mb-3 flex items-start justify-between gap-4">
          <h2 id="dialog-title" className="text-xl font-bold">{title}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close dialog"><X className="h-5 w-5" /></Button>
        </div>
        {children}
      </div>
    </dialog>
  );
}
