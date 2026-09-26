import React from 'react';

/**
 * Official Emblem of India / Ashoka Lion Capital & Maharashtra State Motif
 * Scalable vector SVG with gold/navy authentic government detailing.
 */
export const GovEmblem = ({ size = 36, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 100 100"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`gov-emblem ${className}`}
    aria-label="Government of Maharashtra Official Seal"
  >
    {/* Outer Emblem Ring */}
    <circle cx="50" cy="50" r="47" stroke="currentColor" strokeWidth="2.5" opacity="0.85" />
    <circle cx="50" cy="50" r="43" stroke="currentColor" strokeWidth="1" strokeDasharray="2 3" opacity="0.6" />
    
    {/* Central Pillar Base / Lotus Abacus */}
    <path
      d="M32 72 H68 L64 77 H36 Z"
      fill="currentColor"
      opacity="0.9"
    />
    <rect x="35" y="67" width="30" height="5" rx="1.5" fill="currentColor" opacity="0.8" />
    
    {/* Ashoka Chakra (Central 24-spoke wheel motif) */}
    <circle cx="50" cy="52" r="12" stroke="currentColor" strokeWidth="2" />
    <circle cx="50" cy="52" r="3" fill="currentColor" />
    {/* Spokes */}
    {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
      <line
        key={deg}
        x1="50"
        y1="52"
        x2={50 + 11 * Math.cos((deg * Math.PI) / 180)}
        y2={52 + 11 * Math.sin((deg * Math.PI) / 180)}
        stroke="currentColor"
        strokeWidth="1.2"
        opacity="0.75"
      />
    ))}

    {/* Stylized Lion Capital Top Silhouette */}
    <path
      d="M38 42 C38 35 44 28 50 28 C56 28 62 35 62 42 C62 45 60 48 57 50 C54 48 46 48 43 50 C40 48 38 45 38 42 Z"
      fill="currentColor"
      opacity="0.95"
    />
    {/* Flanking Lions Hints */}
    <path
      d="M28 46 C28 40 33 34 38 36 C37 41 38 45 40 48 C35 49 28 50 28 46 Z"
      fill="currentColor"
      opacity="0.8"
    />
    <path
      d="M72 46 C72 40 67 34 62 36 C63 41 62 45 60 48 C65 49 72 50 72 46 Z"
      fill="currentColor"
      opacity="0.8"
    />

    {/* Base Inscription Banner: Satyameva Jayate arc */}
    <path
      d="M25 84 C38 88 62 88 75 84"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      opacity="0.7"
    />
  </svg>
);

export const TricolorBar = () => (
  <div className="gov-tricolor-bar" role="presentation" aria-hidden="true">
    <div className="tricolor-saffron" />
    <div className="tricolor-white" />
    <div className="tricolor-green" />
  </div>
);
