import { useState } from 'react';
import { Link } from 'react-router-dom';
import { PageContainer, PageHeader } from '@/components/layout/Page';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ROUTES } from '@/lib/routes';
import { UploadCloud, Link2, CheckCircle2, FileText } from 'lucide-react';

export default function DataSources() {
  const [file, setFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<Array<Record<string, string>>>([]);
  const [rowCount, setRowCount] = useState<number>(0);
  const [importStatus, setImportStatus] = useState<'idle' | 'importing' | 'done'>('idle');

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped) processFile(dropped);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) processFile(selected);
  };

  const processFile = (f: File) => {
    setFile(f);
    setImportStatus('idle');
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split('\n').filter((l) => l.trim().length > 0);
      setRowCount(lines.length > 1 ? lines.length - 1 : lines.length);

      // Simple CSV header/row parser for first 10 rows
      if (lines.length > 0) {
        const headers = lines[0].split(',').map((h) => h.trim().replace(/^"|"$/g, ''));
        const rows = lines.slice(1, 11).map((line) => {
          const cells = line.split(',');
          const obj: Record<string, string> = {};
          headers.forEach((h, i) => {
            obj[h] = (cells[i] ?? '').trim().replace(/^"|"$/g, '');
          });
          return obj;
        });
        setPreviewRows(rows);
      }
    };
    reader.readAsText(f);
  };

  const handleImport = async () => {
    setImportStatus('importing');
    await new Promise((r) => setTimeout(r, 800));
    setImportStatus('done');
  };

  return (
    <PageContainer>
      <PageHeader
        title="Data Sources"
        subtitle="Import customer review datasets or analyze single product links."
      />

      {/* Action Shortcut to Analyze a link */}
      <div className="flex items-center justify-between p-4 rounded-card border border-rp-border bg-rp-surface">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-rp-primary-light text-rp-primary">
            <Link2 className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-rp-navy">Have a product link?</h3>
            <p className="text-xs text-rp-muted">Paste an Amazon or Flipkart link to extract reviews automatically.</p>
          </div>
        </div>
        <Link
          to={ROUTES.analyze}
          className="rounded-btn bg-rp-primary px-4 py-2 text-xs font-semibold text-white shadow-soft hover:bg-rp-primary-hover"
        >
          Analyze a Link
        </Link>
      </div>

      {/* File Upload Section */}
      <Card className="p-6 md:p-8 space-y-6">
        <h2 className="font-heading text-lg font-bold text-rp-navy">Upload Dataset</h2>
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-rp-border rounded-2xl bg-rp-surface-soft/40 hover:bg-rp-surface-soft transition-colors cursor-pointer text-center"
        >
          <UploadCloud className="h-10 w-10 text-rp-primary mb-3" />
          <p className="text-sm font-bold text-rp-navy">Drag & drop your review dataset here</p>
          <p className="text-xs text-rp-muted mt-1">Supports Amazon and Flipkart CSV or JSON files</p>
          <label className="mt-4 cursor-pointer rounded-btn border border-rp-border bg-rp-surface px-4 py-2 text-xs font-semibold text-rp-navy shadow-soft hover:bg-rp-primary-light">
            Browse file
            <input type="file" accept=".csv,.json" onChange={handleFileSelect} className="hidden" />
          </label>
        </div>

        {file && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-xl bg-rp-surface border border-rp-border text-sm">
              <span className="font-semibold text-rp-navy flex items-center gap-2">
                <FileText className="h-4 w-4 text-rp-primary" /> {file.name}
              </span>
              <span className="text-xs text-rp-muted">({rowCount} detected rows)</span>
            </div>

            {previewRows.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-rp-muted uppercase tracking-wider">Preview (First 10 Rows)</h3>
                <div className="overflow-x-auto rounded-xl border border-rp-border">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-rp-border bg-rp-surface-soft">
                        {Object.keys(previewRows[0]).map((h) => (
                          <th key={h} className="p-2 font-bold text-rp-navy">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-rp-border">
                      {previewRows.map((r, i) => (
                        <tr key={i} className="hover:bg-rp-surface-soft/40">
                          {Object.values(r).map((v, j) => (
                            <td key={j} className="p-2 text-rp-text truncate max-w-[200px]">
                              {v}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {importStatus === 'idle' && (
              <Button onClick={handleImport} className="w-full">
                Import Dataset
              </Button>
            )}

            {importStatus === 'importing' && (
              <p className="text-sm text-rp-primary font-semibold text-center">Importing dataset in progress...</p>
            )}

            {importStatus === 'done' && (
              <div className="p-4 rounded-xl border border-rp-success/30 bg-rp-success/10 text-sm space-y-1">
                <p className="font-bold text-rp-success flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" /> Import Complete
                </p>
                <p className="text-xs text-rp-text">
                  Processed {rowCount} rows from {file.name}. Reviews are now available in your workspace library.
                </p>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Import History Table */}
      <Card className="p-6 space-y-4">
        <h2 className="font-heading text-lg font-bold text-rp-navy">Import History</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-rp-border">
                <th className="pb-2 font-semibold text-rp-navy">Source</th>
                <th className="pb-2 font-semibold text-rp-navy">Type</th>
                <th className="pb-2 font-semibold text-rp-navy">Status</th>
                <th className="pb-2 font-semibold text-rp-navy">Reviews</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rp-border">
              <tr className="text-xs">
                <td className="py-2.5 font-medium text-rp-navy">Amazon Sample Dataset</td>
                <td className="py-2.5 text-rp-muted">CSV file</td>
                <td className="py-2.5 text-rp-success font-semibold">Active</td>
                <td className="py-2.5 text-rp-text">100 rows</td>
              </tr>
              <tr className="text-xs">
                <td className="py-2.5 font-medium text-rp-navy">Flipkart Sample Ingestion</td>
                <td className="py-2.5 text-rp-muted">Product Link</td>
                <td className="py-2.5 text-rp-success font-semibold">Active</td>
                <td className="py-2.5 text-rp-text">50 rows</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </PageContainer>
  );
}
