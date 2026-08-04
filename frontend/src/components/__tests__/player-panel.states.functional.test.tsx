import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { PlayerPanel } from '../ui';
import type { RawStatePlayer } from '@/lib/types';

function makePlayer(overrides?: Partial<RawStatePlayer>): RawStatePlayer {
  return {
    player_id: 1,
    username: 'alice',
    display_name: 'Alice',
    active: false,
    is_busted: false,
    score: 0,
    total_score: 12,
    unique_numbers: 1,
    cards: [
      {
        card_name: '0',
        value: 0,
        effect_type: 'number',
        effect_payload: '',
      },
    ],
    ...overrides,
  };
}

describe('PlayerPanel state rendering', () => {
  it('renders active state as Your turn when the player is active and not busted', () => {
    const activePlayer = makePlayer({ active: true, is_busted: false, score: 7 });

    render(
      <PlayerPanel
        player={activePlayer}
        isActive={true}
        isBust={false}
        targetScore={200}
        justDrew={false}
      />,
    );

    expect(screen.getByText('Your turn')).toBeInTheDocument();
    expect(screen.queryByText('Bust')).not.toBeInTheDocument();
  });

  it('renders Bust when is_busted is true', () => {
    const bustedPlayer = makePlayer({ is_busted: true, score: 0 });

    render(
      <PlayerPanel
        player={bustedPlayer}
        isActive={false}
        isBust={true}
        targetScore={200}
        justDrew={false}
      />,
    );

    expect(screen.getByText('Bust')).toBeInTheDocument();
  });

  it('does not render Bust for a stayed zero-score player', () => {
    const stayedZeroPlayer = makePlayer({ is_busted: false, active: false, score: 0 });

    render(
      <PlayerPanel
        player={stayedZeroPlayer}
        isActive={false}
        isBust={false}
        targetScore={200}
        justDrew={false}
      />,
    );

    expect(screen.queryByText('Bust')).not.toBeInTheDocument();
    expect(screen.getByText('Waiting')).toBeInTheDocument();
  });
});
