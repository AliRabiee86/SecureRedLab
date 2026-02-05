/**
 * SecureRedLab - Badge Component Tests
 * Phase 8.5 - Testing & Polish
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Badge from '@/components/common/Badge';

describe('Badge Component', () => {
  it('renders badge with children', () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText('Test Badge')).toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { container: successContainer } = render(<Badge variant="success">Success</Badge>);
    expect(successContainer.querySelector('span')).toHaveClass('bg-green-500/10', 'text-green-400');

    const { container: dangerContainer } = render(<Badge variant="danger">Danger</Badge>);
    expect(dangerContainer.querySelector('span')).toHaveClass('bg-red-500/10', 'text-red-400');

    const { container: warningContainer } = render(<Badge variant="warning">Warning</Badge>);
    expect(warningContainer.querySelector('span')).toHaveClass('bg-yellow-500/10', 'text-yellow-400');

    const { container: infoContainer } = render(<Badge variant="info">Info</Badge>);
    expect(infoContainer.querySelector('span')).toHaveClass('bg-blue-500/10', 'text-blue-400');
  });

  it('applies custom className', () => {
    const { container } = render(<Badge className="custom-class">Custom</Badge>);
    expect(container.querySelector('span')).toHaveClass('custom-class');
  });
});
