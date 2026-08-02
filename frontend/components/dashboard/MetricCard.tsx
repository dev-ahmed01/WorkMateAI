import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, trend }) => {
  return (
    <div className="p-6 bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
      <span className="text-sm font-medium text-gray-500">{title}</span>
      <div className="mt-2 flex items-baseline justify-between">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        {change && (
          <span
            className={	ext-xs font-semibold px-2 py-0.5 rounded-full \}
          >
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
