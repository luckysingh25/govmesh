import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loader = ({ text = "Loading..." }) => (
  <div className="flex flex-col items-center justify-center gap-4 py-8 text-muted fade-in">
    <Loader2 className="spin" size={32} />
    <p>{text}</p>
  </div>
);
