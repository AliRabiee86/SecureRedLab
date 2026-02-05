/**
 * SecureRedLab - Button Component Tests
 * Phase 8.5 - Testing & Polish
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/common/Button';

describe('Button Component', () => {
  it('renders button with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant classes correctly', () => {
    const { container: primaryContainer } = render(<Button variant="primary">Primary</Button>);
    expect(primaryContainer.querySelector('button')).toHaveClass('bg-blue-600');

    const { container: secondaryContainer } = render(<Button variant="secondary">Secondary</Button>);
    expect(secondaryContainer.querySelector('button')).toHaveClass('bg-gray-600');
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByText('Disabled') as HTMLButtonElement;
    expect(button).toBeDisabled();
    expect(button).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('shows loading spinner when loading prop is true', () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByText('Loading') as HTMLButtonElement;
    expect(button).toBeDisabled();
    // Check for Loader2 icon (lucide-react renders as svg)
    const svg = button.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { container: smContainer } = render(<Button size="sm">Small</Button>);
    expect(smContainer.querySelector('button')).toHaveClass('px-3', 'py-1.5', 'text-sm');

    const { container: lgContainer } = render(<Button size="lg">Large</Button>);
    expect(lgContainer.querySelector('button')).toHaveClass('px-6', 'py-3', 'text-lg');
  });
});
