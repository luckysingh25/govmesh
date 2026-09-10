import React from 'react';
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { ThemeProvider, useTheme } from './ThemeContext';

const ThemeProbe = () => {
  const { theme, toggleTheme } = useTheme();
  return <button onClick={toggleTheme}>{theme}</button>;
};

describe('ThemeProvider', () => {
  afterEach(cleanup);

  beforeEach(() => {
    window.localStorage.clear();
    delete document.documentElement.dataset.theme;
  });

  it('defaults to dark and persists a light-mode selection', async () => {
    render(<ThemeProvider><ThemeProbe /></ThemeProvider>);

    expect(screen.getByRole('button')).toHaveTextContent('dark');
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => expect(document.documentElement).toHaveAttribute('data-theme', 'light'));
    expect(window.localStorage.getItem('govmesh-theme')).toBe('light');
  });

  it('restores a saved light-mode selection', () => {
    window.localStorage.setItem('govmesh-theme', 'light');
    render(<ThemeProvider><ThemeProbe /></ThemeProvider>);
    expect(screen.getByRole('button')).toHaveTextContent('light');
  });
});
