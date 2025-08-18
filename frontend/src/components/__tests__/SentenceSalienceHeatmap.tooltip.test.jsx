import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SentenceSalienceHeatmap from '../SentenceSalienceHeatmap.jsx';

describe('SentenceSalienceHeatmap Tooltip', () => {
    const mockSentences = [
        { text: 'First sentence with high salience.', salience: 0.9 },
        { text: 'Second sentence with medium salience.', salience: 0.5 }
    ];

    const mockMicroSpans = [
        [
            { text: 'high salience', weight: 0.85, start: 20, end: 32, method: 'ngram-basic' },
            { text: 'First sentence', weight: 0.75, start: 0, end: 14, method: 'ngram-basic' }
        ],
        [
            { text: 'medium salience', weight: 0.6, start: 22, end: 37, method: 'ngram-basic' }
        ]
    ];

    it('renders tooltip data attributes when micro-spans are provided', () => {
        render(
            <SentenceSalienceHeatmap
                sentences={mockSentences}
                microSpans={mockMicroSpans}
                showMicroSpans={true}
            />
        );

        // Check that the first sentence has tooltip data attribute
        const firstSentence = screen.getByText('First sentence with high salience.');
        expect(firstSentence).toHaveAttribute('data-tooltip-id', 'sentence-tooltip-0');
        expect(firstSentence).toHaveStyle('cursor: help');
    });

    it('does not add tooltip attributes when showMicroSpans is false', () => {
        render(
            <SentenceSalienceHeatmap
                sentences={mockSentences}
                microSpans={mockMicroSpans}
                showMicroSpans={false}
            />
        );

        const firstSentence = screen.getByText('First sentence with high salience.');
        expect(firstSentence).not.toHaveAttribute('data-tooltip-id');
        expect(firstSentence).toHaveStyle('cursor: default');
    });

    it('does not add tooltip attributes when no micro-spans provided', () => {
        render(
            <SentenceSalienceHeatmap
                sentences={mockSentences}
                microSpans={null}
                showMicroSpans={true}
            />
        );

        const firstSentence = screen.getByText('First sentence with high salience.');
        expect(firstSentence).not.toHaveAttribute('data-tooltip-id');
    });

    it('renders tooltip elements for sentences with micro-spans', async () => {
        const { container } = render(
            <SentenceSalienceHeatmap
                sentences={mockSentences}
                microSpans={mockMicroSpans}
                showMicroSpans={true}
            />
        );
 
        // Trigger tooltip rendering via user interaction (hover)
        const firstSentence = screen.getByText('First sentence with high salience.');
        const secondSentence = screen.getByText('Second sentence with medium salience.');
        fireEvent.mouseOver(firstSentence);
        fireEvent.mouseOver(secondSentence);
 
        // Wait for tooltip content to appear in the DOM
        await screen.findByText(/Micro-spans \(\d+\)/);
 
        // Check that tooltip elements are rendered
        const tooltips = container.querySelectorAll('[id^="sentence-tooltip-"]');
        expect(tooltips).toHaveLength(2); // Two sentences with micro-spans
    });

    it('displays correct micro-span count in tooltip content', async () => {
        render(
            <SentenceSalienceHeatmap
                sentences={mockSentences}
                microSpans={mockMicroSpans}
                showMicroSpans={true}
            />
        );
 
        // Trigger tooltip render for the first sentence
        const firstSentence = screen.getByText('First sentence with high salience.');
        fireEvent.mouseOver(firstSentence);
 
        // Wait for the tooltip content to appear and assert count/texts
        expect(await screen.findByText('Micro-spans (2)')).toBeInTheDocument();
        
        // Check that micro-span texts are rendered
        expect(screen.getByText('"high salience"')).toBeInTheDocument();
        expect(screen.getByText('"First sentence"')).toBeInTheDocument();
    });
});