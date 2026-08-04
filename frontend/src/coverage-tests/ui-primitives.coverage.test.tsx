import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Button, Modal, PlayerPanel } from '../components/ui';
import type { RawStatePlayer } from '@/lib/types';

function makePlayer(overrides?: Partial<RawStatePlayer>): RawStatePlayer {
  return {
    player_id: 1,
    username: 'alice',
    display_name: 'Alice',
    active: true,
    is_busted: false,
    score: 9,
    total_score: 42,
    unique_numbers: 4,
    cards: [
      { card_name: '4', value: 4, effect_type: 'number', effect_payload: '' },
      { card_name: '9', value: 9, effect_type: 'number', effect_payload: '' },
      { card_name: '+2', value: null, effect_type: 'modifier', effect_payload: '+2' },
    ],
    ...overrides,
  };
}

describe('UI primitive coverage behavior', () => {
  it('applies Button classes and loading/disabled behavior', () => {
    const { rerender } = render(
      <Button variant="primary" block small>
        Play
      </Button>,
    );

    const base = screen.getByRole('button', { name: 'Play' });
    expect(base.className).toContain('btn');
    expect(base.className).toContain('primary');
    expect(base.className).toContain('block');
    expect(base.className).toContain('small');

    rerender(<Button loading>Loading</Button>);
    const loading = screen.getByRole('button', { name: 'Loading' });
    expect(loading).toBeDisabled();
    expect(loading.querySelector('.btnSpinner')).not.toBeNull();
  });

  it('Modal dismisses on overlay click and escape key', async () => {
    function Harness() {
      const [open, setOpen] = React.useState(true);
      return open ? (
        <Modal title="Test Modal" onClose={() => setOpen(false)}>
          <button type="button">Inside</button>
        </Modal>
      ) : (
        <p>Closed</p>
      );
    }

    const first = render(<Harness />);
    fireEvent.click(screen.getByRole('presentation'));
    await screen.findByText('Closed');
    first.unmount();

    render(<Harness />);
    await screen.findByRole('dialog', { name: 'Test Modal' });
    fireEvent.keyDown(window, { key: 'Escape' });
    await screen.findByText('Closed');
  });

  it('Modal focus trap cycles between first and last controls', async () => {
    render(
      <Modal title="Focus Modal" onClose={() => undefined}>
        <button type="button">First</button>
        <button type="button">Last</button>
      </Modal>,
    );

    const dialog = screen.getByRole('dialog', { name: 'Focus Modal' });
    const first = within(dialog).getByRole('button', { name: 'Close dialog' });
    const last = within(dialog).getByRole('button', { name: 'Last' });

    await waitFor(() => expect(document.activeElement).toBe(first));

    last.focus();
    fireEvent.keyDown(window, { key: 'Tab' });
    expect(document.activeElement).toBe(first);

    first.focus();
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(last);
  });

  it('PlayerPanel covers score layout and high-risk warning branch', () => {
    const { rerender } = render(
      <PlayerPanel
        player={makePlayer()}
        isActive={true}
        isBust={false}
        targetScore={200}
        justDrew={false}
      />,
    );

    expect(screen.getByLabelText('Alice panel')).toBeInTheDocument();
    expect(screen.getByText('Round')).toBeInTheDocument();
    expect(screen.getByText('Total / 200')).toBeInTheDocument();
    expect(screen.getByText('Your turn')).toBeInTheDocument();
    expect(screen.getByText('Unique numbers: 4 / 7')).toBeInTheDocument();

    rerender(
      <PlayerPanel
        player={makePlayer({
          unique_numbers: 6,
          cards: [
            { card_name: '1', value: 1, effect_type: 'number', effect_payload: '' },
            { card_name: '2', value: 2, effect_type: 'number', effect_payload: '' },
            { card_name: '3', value: 3, effect_type: 'number', effect_payload: '' },
            { card_name: '4', value: 4, effect_type: 'number', effect_payload: '' },
            { card_name: '5', value: 5, effect_type: 'number', effect_payload: '' },
            { card_name: '6', value: 6, effect_type: 'number', effect_payload: '' },
          ],
        })}
        isActive={false}
        isBust={false}
        targetScore={200}
        justDrew={false}
      />,
    );

    expect(screen.getByText(/Duplicate danger/)).toBeInTheDocument();
  });
});
