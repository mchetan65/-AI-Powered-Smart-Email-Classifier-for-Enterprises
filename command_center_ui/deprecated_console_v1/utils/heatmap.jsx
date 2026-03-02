import React from 'react';
import { Tooltip as MuiTooltip } from '@mui/material';

const hexToRgba = (hex, alpha) => {
    let r = 0, g = 0, b = 0;
    if (hex.length === 4) {
        r = parseInt(hex[1] + hex[1], 16);
        g = parseInt(hex[2] + hex[2], 16);
        b = parseInt(hex[3] + hex[3], 16);
    } else if (hex.length === 7) {
        r = parseInt(hex.substring(1, 3), 16);
        g = parseInt(hex.substring(3, 5), 16);
        b = parseInt(hex.substring(5, 7), 16);
    }
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const renderHeatmap = (text, scores, baseColor = '#ef4444') => {
    if (!scores?.length) return text;
    return text.split(' ').map((word, i) => {
        const clean = word.replace(/[^\w]/g,"");
        // Normalize word implementation might differ, keeping simple find
        const match = scores.find(s => s.word === word || s.word === clean);
        if (match) {
            return (
                <span key={i} style={{ 
                    backgroundColor: hexToRgba(baseColor, 0.3), 
                    fontWeight: 700, padding: '0 2px', borderRadius: 4
                }}>{word} </span>
            );
        }
        return word + ' ';
    });
};
