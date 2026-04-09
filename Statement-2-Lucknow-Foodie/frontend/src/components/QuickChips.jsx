import React from 'react';

const SUGGESTIONS = [
    "Best biryani near campus",
    "Veg places under ₹200",
    "Late night food options",
    "Best date night spot",
    "Closest open right now",
    "Budget breakfast places"
];

export const QuickChips = ({ onSelect }) => {
    return (
        <div className="flex flex-wrap gap-2 mb-4">
            {SUGGESTIONS.map((s, idx) => (
                <button
                    key={idx}
                    onClick={() => onSelect(s)}
                    className="text-xs bg-orange-50 hover:bg-orange-100 text-primary border border-orange-200 px-3 py-1.5 rounded-full transition-colors font-medium whitespace-nowrap shadow-sm"
                >
                    {s}
                </button>
            ))}
        </div>
    );
};
