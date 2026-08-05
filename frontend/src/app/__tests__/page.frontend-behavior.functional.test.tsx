import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import type { ActionResult, GameResults, GameSummary, Player, RawGameState } from '@/lib/types';

const mockFns = vi.hoisted(() => ({
  listPlayers: vi.fn<() => Promise<Player[]>>(),
  listGames: vi.fn<() => Promise<GameSummary[]>>(),
  createPlayer: vi.fn(),
  updatePlayer: vi.fn(),
  createGame: vi.fn(),
  joinGame: vi.fn(),
  removePlayer: vi.fn(),
  startRound: vi.fn(),
  getState: vi.fn<() => Promise<RawGameState>>(),
  closeGame: vi.fn(),
  getResults: vi.fn<() => Promise<GameResults>>(),
  takeAction: vi.fn<() => Promise<ActionResult>>(),
}));

vi.mock('../../lib/api', () => ({
  api: {
    listPlayers: mockFns.listPlayers,
    listGames: mockFns.listGames,
    createPlayer: mockFns.createPlayer,
    updatePlayer: mockFns.updatePlayer,
    createGame: mockFns.createGame,
    joinGame: mockFns.joinGame,
    removePlayer: mockFns.removePlayer,
    startRound: mockFns.startRound,
    getState: mockFns.getState,
    closeGame: mockFns.closeGame,
    getResults: mockFns.getResults,
    takeAction: mockFns.takeAction,
  },
}));

const mockApi = mockFns;

import HomePage from '../page';

function makeState(overrides?: Partial<RawGameState>): RawGameState {
  return {
    game_id: 1,
    game_code: 'FLIP1234',
    status: 'pending',
    target_score: 200,
    round_id: null,
    round_ended: false,
    active_player_count: 2,
    deck_remaining: 92,
    current_turn: null,
    players: [
      {
        player_id: 1,
        username: 'alice',
        display_name: 'Alice',
        active: true,
        is_busted: false,
        score: 0,
        total_score: 0,
        unique_numbers: 1,
        cards: [{ card_name: '2', value: 2, effect_type: 'number', effect_payload: '' }],
      },
      {
        player_id: 2,
        username: 'bob',
        display_name: 'Bob',
        active: true,
        is_busted: false,
        score: 0,
        total_score: 0,
        unique_numbers: 1,
        cards: [{ card_name: '4', value: 4, effect_type: 'number', effect_payload: '' }],
      },
    ],
    ...overrides,
  };
}

const basePlayers: Player[] = [
  { id: 1, username: 'alice', display_name: 'Alice' },
  { id: 2, username: 'bob', display_name: 'Bob' },
];

beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

beforeEach(() => {
  vi.useRealTimers();
  vi.clearAllMocks();
  window.localStorage.clear();

  mockApi.listPlayers.mockResolvedValue(basePlayers);
  mockApi.listGames.mockResolvedValue([]);
  mockApi.createPlayer.mockResolvedValue(basePlayers[0]);
  mockApi.updatePlayer.mockResolvedValue(basePlayers[0]);
  mockApi.createGame.mockResolvedValue({ id: 1, game_code: 'FLIP1234', status: 'pending' });
  mockApi.joinGame.mockResolvedValue({ status: 'joined', game_player_id: 1 });
  mockApi.removePlayer.mockResolvedValue(makeState());
  mockApi.startRound.mockResolvedValue({ round_id: 1, turn_id: 1, state: makeState({ status: 'active', round_id: 1, current_turn: 1 }) });
  mockApi.getState.mockResolvedValue(makeState());
  mockApi.closeGame.mockResolvedValue(null);
  mockApi.getResults.mockResolvedValue({
    game_id: 1,
    status: 'finished',
    target_score: 200,
    winner: { player_id: 1, username: 'alice', display_name: 'Alice', total_score: 200 },
    standings: [
      { player_id: 1, username: 'alice', display_name: 'Alice', seat_number: 1, total_score: 200, is_busted: false },
      { player_id: 2, username: 'bob', display_name: 'Bob', seat_number: 2, total_score: 120, is_busted: false },
    ],
  });
  mockApi.takeAction.mockResolvedValue({ round_ended: false, bust: false });
});

async function renderToLobby() {
  render(<HomePage />);
  await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });
}

describe('Frontend app functional behavior', () => {
  it('routes between splash, lobby, create, and waiting screens', async () => {
    mockApi.listGames.mockResolvedValue([{ id: 7, game_code: 'FLIP0007', status: 'pending' }]);
    mockApi.getState.mockResolvedValue(makeState({ game_id: 7, game_code: 'FLIP0007', status: 'pending' }));

    render(<HomePage />);
    expect(screen.getByText('Shuffling the deck…')).toBeInTheDocument();

    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: 'Create game' }));
    expect(screen.getByRole('heading', { name: 'New game' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Back to lobby' }));
    expect(screen.getByRole('heading', { name: 'Open games' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByRole('heading', { name: 'Waiting room' });
  });

  it('routes to active and game over states from authoritative backend state', async () => {
    const activeState = makeState({
      game_id: 3,
      game_code: 'FLIP0003',
      status: 'active',
      round_id: 1,
      round_ended: false,
      current_turn: 1,
    });

    mockApi.listGames.mockResolvedValue([{ id: 3, game_code: 'FLIP0003', status: 'active' }]);
    mockApi.getState.mockResolvedValue(activeState);

    const first = render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByRole('heading', { name: "Alice's turn" });
    first.unmount();

    window.localStorage.setItem('flip7.gameId', '9');
    mockApi.getState.mockResolvedValueOnce(makeState({ game_id: 9, game_code: 'FLIP0009', status: 'finished' }));

    render(<HomePage />);
    await screen.findByText('Game over', {}, { timeout: 4000 });
    expect(screen.getByText('Alice wins!')).toBeInTheDocument();
  });

  it('shows loading lockout in the action panel while an action is pending', async () => {
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 });
    mockApi.getState.mockResolvedValue(activeState);
    window.localStorage.setItem('flip7.gameId', '1');

    let resolveAction: (value: ActionResult) => void = () => undefined;
    const actionPromise = new Promise<ActionResult>((resolve) => {
      resolveAction = resolve;
    });
    mockApi.takeAction.mockReturnValue(actionPromise);

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    const hitButton = await screen.findByRole('button', { name: /Hit/ });
    fireEvent.click(hitButton);

    await waitFor(() => expect(hitButton).toBeDisabled());

    resolveAction({ round_ended: false, bust: false });

    await waitFor(() => expect(hitButton).toBeEnabled());
  });

  it('supports target selection presentation and cancel behavior for Freeze', async () => {
    const activeWithFreeze = makeState({
      status: 'active',
      round_id: 1,
      current_turn: 1,
      players: [
        {
          player_id: 1,
          username: 'alice',
          display_name: 'Alice',
          active: true,
          is_busted: false,
          score: 0,
          total_score: 0,
          unique_numbers: 1,
          cards: [
            { card_name: '3', value: 3, effect_type: 'number', effect_payload: '' },
            { card_name: 'Freeze', value: null, effect_type: 'action', effect_payload: 'freeze' },
          ],
        },
        {
          player_id: 2,
          username: 'bob',
          display_name: 'Bob',
          active: true,
          is_busted: false,
          score: 0,
          total_score: 0,
          unique_numbers: 1,
          cards: [{ card_name: '4', value: 4, effect_type: 'number', effect_payload: '' }],
        },
      ],
    });

    mockApi.getState.mockResolvedValue(activeWithFreeze);
    window.localStorage.setItem('flip7.gameId', '1');

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    fireEvent.click(await screen.findByRole('button', { name: /Freeze/ }));
    expect(screen.getByRole('heading', { name: 'Choose target for Freeze' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: 'Choose target for Freeze' })).not.toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: /Hit/ })).toBeInTheDocument();
  });

  it('opens/closes rules modal and restores focus to the trigger', async () => {
    await renderToLobby();

    const trigger = screen.getByRole('button', { name: 'How to play' });
    trigger.focus();
    expect(document.activeElement).toBe(trigger);
    fireEvent.click(trigger);

    const dialog = await screen.findByRole('dialog', { name: 'How to Play' });
    const closeDialogButton = within(dialog).getByRole('button', { name: 'Close dialog' });

    await waitFor(() => expect(document.activeElement).toBe(closeDialogButton));

    fireEvent.click(within(dialog).getByRole('button', { name: 'Got it' }));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'How to Play' })).not.toBeInTheDocument());
    expect(document.activeElement).toBe(trigger);
  });

  it('opens/closes confirm-leave modal and restores focus to the trigger', async () => {
    mockApi.getState.mockResolvedValue(makeState({ status: 'pending', round_id: null, current_turn: null }));
    window.localStorage.setItem('flip7.gameId', '1');

    render(<HomePage />);
    await screen.findByRole('heading', { name: 'Waiting room' }, { timeout: 4000 });

    const trigger = await screen.findByLabelText('Close game', {}, { timeout: 4000 });
    trigger.focus();
    expect(document.activeElement).toBe(trigger);
    fireEvent.click(trigger);

    const dialog = await screen.findByRole('dialog', { name: 'Close game?' });
    const closeDialogButton = within(dialog).getByRole('button', { name: 'Close dialog' });

    await waitFor(() => expect(document.activeElement).toBe(closeDialogButton));

    fireEvent.click(within(dialog).getByRole('button', { name: 'Keep playing' }));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Close game?' })).not.toBeInTheDocument());
    expect(document.activeElement).toBe(trigger);
  });

  it('shows disconnect modal on network error and retries successfully', async () => {
    const networkError = Object.assign(new Error('Network request failed'), { code: 'network_error' });
    mockApi.listPlayers.mockRejectedValueOnce(networkError).mockResolvedValueOnce(basePlayers);
    mockApi.listGames.mockRejectedValueOnce(networkError).mockResolvedValueOnce([]);

    render(<HomePage />);
    await screen.findByRole('dialog', { name: 'Connection lost' }, { timeout: 4000 });

    const dialog = screen.getByRole('dialog', { name: 'Connection lost' });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reconnect' }));

    await waitFor(() => {
      expect(screen.queryByRole('dialog', { name: 'Connection lost' })).not.toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Create game' })).toBeInTheDocument();
  });

  it('shows round summary modal and next-round interaction after round end', async () => {
    const activeState = makeState({ status: 'active', round_id: 2, current_turn: 1, round_ended: false });
    const postRoundState = makeState({ status: 'active', round_id: 2, current_turn: null, round_ended: true });

    mockApi.getState.mockResolvedValueOnce(activeState).mockResolvedValue(postRoundState);
    mockApi.takeAction.mockResolvedValue({
      round_ended: true,
      round_summary: [
        { player_id: 1, username: 'alice', display_name: 'Alice', score: 10, total_score: 50 },
        { player_id: 2, username: 'bob', display_name: 'Bob', score: 5, total_score: 45 },
      ],
    });
    mockApi.startRound.mockResolvedValue({
      round_id: 3,
      turn_id: 7,
      state: makeState({ status: 'active', round_id: 3, current_turn: 1, round_ended: false }),
    });

    window.localStorage.setItem('flip7.gameId', '1');
    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    fireEvent.click(await screen.findByRole('button', { name: /Stay/ }));
    const summaryDialog = await screen.findByRole('dialog', { name: 'Round Summary' });
    expect(within(summaryDialog).getAllByText('Banked this round').length).toBeGreaterThan(0);

    fireEvent.click(within(summaryDialog).getByRole('button', { name: 'Next round' }));
    await waitFor(() => expect(mockApi.startRound).toHaveBeenCalledTimes(1));
  });

  it('syncs another device\'s turn into the board via background polling', async () => {
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 });
    mockApi.getState.mockResolvedValue(activeState);
    window.localStorage.setItem('flip7.gameId', '1');

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    // Another device advances play to Bob; polling should pick it up.
    mockApi.getState.mockResolvedValue(
      makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 2 }),
    );

    await screen.findByRole('heading', { name: "Bob's turn" }, { timeout: 6000 });
  }, 15000);

  it('follows the waiting room into the board when a round starts elsewhere', async () => {
    mockApi.getState.mockResolvedValue(makeState({ status: 'pending', round_id: null, current_turn: null }));
    window.localStorage.setItem('flip7.gameId', '1');

    render(<HomePage />);
    await screen.findByRole('heading', { name: 'Waiting room' }, { timeout: 4000 });

    // A round is started on another device.
    mockApi.getState.mockResolvedValue(
      makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 }),
    );

    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 6000 });
  }, 15000);
});
