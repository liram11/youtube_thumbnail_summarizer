import React from 'react';

interface TooltipProps {
  summary: string;
}

const Tooltip: React.FC<TooltipProps> = ({ summary }) => {
  return (
    <div className="tooltip">
      <span className="tooltip-text">{summary}</span>
    </div>
  );
};

export default Tooltip;