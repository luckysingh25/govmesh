import React from 'react';

export const Card = ({ title, children, className = '', action }) => (
  <div className={`card ${className}`}>
    {(title || action) && (
      <div className="card-header">
        {title && <h3 className="card-title">{title}</h3>}
        {action && <div>{action}</div>}
      </div>
    )}
    <div className="card-content">
      {children}
    </div>
  </div>
);
