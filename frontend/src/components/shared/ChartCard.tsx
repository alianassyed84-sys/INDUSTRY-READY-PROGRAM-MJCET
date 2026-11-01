import { useState, type ReactNode } from 'react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/states';
import { Table, BarChart2 } from 'lucide-react';

export interface ChartTableColumn {
  key: string;
  header: string;
}

export interface ChartCardProps {
  title: string;
  subtitle?: string;
  summary: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  tableData?: Array<Record<string, ReactNode>>;
  columns?: ChartTableColumn[];
  isEmpty?: boolean;
  emptyMessage?: string;
}

/**
 * ChartCard container conforming to FRONTEND_SPEC.md v4:
 * - Plain words takeaway title ("Most reviews are positive")
 * - Labelled axes & tooltip & legend
 * - "View as table" toggle when tableData is provided
 * - Plain empty state when not enough data
 */
export function ChartCard({
  title,
  subtitle,
  summary,
  action,
  children,
  className,
  tableData,
  columns,
  isEmpty = false,
  emptyMessage = 'Not enough data to draw this chart.',
}: ChartCardProps) {
  const [showTable, setShowTable] = useState(false);

  const canShowTable = !!(tableData && tableData.length > 0 && columns && columns.length > 0);

  const tableToggleAction = canShowTable ? (
    <div className="flex items-center gap-2">
      {action}
      <Button
        variant="ghost"
        onClick={() => setShowTable(!showTable)}
        aria-label={showTable ? 'View as chart' : 'View as table'}
        className="text-xs h-8 px-2.5"
      >
        {showTable ? (
          <>
            <BarChart2 className="h-3.5 w-3.5 mr-1" aria-hidden="true" /> View chart
          </>
        ) : (
          <>
            <Table className="h-3.5 w-3.5 mr-1" aria-hidden="true" /> View as table
          </>
        )}
      </Button>
    </div>
  ) : (
    action
  );

  return (
    <Card className={className} data-reveal>
      <CardHeader title={title} subtitle={subtitle} action={tableToggleAction} />
      {isEmpty ? (
        <div className="py-6">
          <EmptyState title="No chart data" description={emptyMessage} />
        </div>
      ) : showTable && canShowTable ? (
        <div className="overflow-x-auto p-4">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-rp-border">
                {columns.map((col) => (
                  <th key={col.key} className="pb-2 font-semibold text-rp-navy">
                    {col.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-rp-border/50">
              {tableData.map((row, idx) => (
                <tr key={idx} className="hover:bg-rp-surface-soft/50">
                  {columns.map((col) => (
                    <td key={col.key} className="py-2 text-rp-text">
                      {row[col.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <>
          <div role="img" aria-label={summary}>{children}</div>
          <p className="sr-only">{summary}</p>
        </>
      )}
    </Card>
  );
}
