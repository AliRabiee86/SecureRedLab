/**
 * SecureRedLab - Card Component Tests
 * Phase 8.5 - Testing & Polish
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from '@/components/common/Card';

describe('Card Component', () => {
  it('renders card with children', () => {
    render(<Card>Test Content</Card>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders card with title', () => {
    render(<Card title="Test Title">Content</Card>);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-card">Content</Card>);
    expect(container.querySelector('.custom-card')).toBeInTheDocument();
  });

  it('renders without title when not provided', () => {
    const { container } = render(<Card>Just Content</Card>);
    expect(container.querySelector('h3')).not.toBeInTheDocument();
  });
});
