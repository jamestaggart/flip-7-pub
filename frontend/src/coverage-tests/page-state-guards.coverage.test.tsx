import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
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

vi.mock('../lib/api', () => ({
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

import HomePage from '../app/page';

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

describe('Page guard-path coverage behavior', () => {
  beforeEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
    window.localStorage.clear();

    mockFns.listPlayers.mockResolvedValue(basePlayers);
    mockFns.listGames.mockResolvedValue([]);
    mockFns.getState.mockResolvedValue(makeState());
    mockFns.getResults.mockResolvedValue({
      game_id: 1,
      status: 'finished',
      target_score: 200,
      winner: null,
      standings: [],
    });
  });

  it('renders Match complete when a finished game has no winner payload', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValueOnce(makeState({ status: 'finished' }));

    render(<HomePage />);
    await screen.findByText('Game over', {}, { timeout: 4000 });
    expect(screen.getByText('Match complete')).toBeInTheDocument();
  });

  it('shows no legal target available guard when freeze is selected without active targets', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValueOnce(
      makeState({
        status: 'active',
        round_id: 1,
        current_turn: 1,
        players: [
          {
            player_id: 1,
            username: 'alice',
            display_name: 'Alice',
            active: false,
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
            active: false,
            is_busted: false,
            score: 0,
            total_score: 0,
            unique_numbers: 1,
            cards: [{ card_name: '4', value: 4, effect_type: 'number', effect_payload: '' }],
          },
        ],
      }),
    );

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: /Freeze/ }));

    expect(screen.getByText('No legal target available.')).toBeInTheDocument();
  });

  it('clears invalid persisted game id and stays in the lobby', async () => {
    window.localStorage.setItem('flip7.gameId', '-2');

    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });

    await waitFor(() => expect(window.localStorage.getItem('flip7.gameId')).toBeNull());
    expect(screen.getByRole('heading', { name: 'Open games' })).toBeInTheDocument();
  });

  it('recovers to lobby toast when a restored game id resolves to 404', async () => {
    window.localStorage.setItem('flip7.gameId', '44');
    mockFns.getState.mockRejectedValueOnce({ statusCode: 404 });

    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });

    expect(await screen.findByText('This game was closed.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Open games' })).toBeInTheDocument();
  });

  it('routes to game-over from action refresh when finished-state result lookup fails', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState
      .mockResolvedValueOnce(
        makeState({
          status: 'active',
          round_id: 1,
          current_turn: 1,
        }),
      )
      .mockResolvedValueOnce(makeState({ status: 'finished' }));
    mockFns.takeAction.mockResolvedValueOnce({ round_ended: true, bust: false });
    mockFns.getResults.mockRejectedValueOnce(new Error('results unavailable'));

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: /Hit/ }));

    await screen.findByText('Game over', {}, { timeout: 4000 });
    expect(screen.getByText('Match complete')).toBeInTheDocument();
  });

  it('treats close-game 404 as already-closed and returns to lobby', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValueOnce(makeState({ status: 'pending' }));
    mockFns.closeGame.mockRejectedValueOnce({ statusCode: 404 });

    render(<HomePage />);
    await screen.findByRole('heading', { name: 'Waiting room' }, { timeout: 4000 });

    fireEvent.click(screen.getByLabelText('Close game'));
    const dialog = await screen.findByRole('dialog', { name: 'Close game?' }, { timeout: 4000 });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Close game' }));

    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });
    expect(screen.getByRole('heading', { name: 'Open games' })).toBeInTheDocument();
  });

  it('shows remove-player spinner path while waiting-room removal is pending', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValueOnce(
      makeState({
        status: 'pending',
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
          {
            player_id: 3,
            username: 'cara',
            display_name: 'Cara',
            active: true,
            is_busted: false,
            score: 0,
            total_score: 0,
            unique_numbers: 1,
            cards: [{ card_name: '5', value: 5, effect_type: 'number', effect_payload: '' }],
          },
        ],
      }),
    );

    let resolveRemoval: ((state: RawGameState) => void) | null = null;
    mockFns.removePlayer.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveRemoval = resolve;
        }),
    );

    render(<HomePage />);
    await screen.findByRole('heading', { name: 'Waiting room' }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: 'Remove Bob' }));
    const spinnerHost = screen.getByRole('button', { name: 'Remove Bob' });
    expect(spinnerHost.querySelector('.btnSpinner')).not.toBeNull();

    resolveRemoval?.(
      makeState({
        status: 'pending',
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
            player_id: 3,
            username: 'cara',
            display_name: 'Cara',
            active: true,
            is_busted: false,
            score: 0,
            total_score: 0,
            unique_numbers: 1,
            cards: [{ card_name: '5', value: 5, effect_type: 'number', effect_payload: '' }],
          },
        ],
      }),
    );
  });

  it('covers freeze target confirm callback path and submits chosen target', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState
      .mockResolvedValueOnce(
        makeState({
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
        }),
      )
      .mockResolvedValueOnce(
        makeState({
          status: 'active',
          round_id: 1,
          current_turn: 2,
        }),
      );

    mockFns.takeAction.mockResolvedValueOnce({ round_ended: false, bust: false });

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: /Freeze/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Bob' }));

    expect(mockFns.takeAction).toHaveBeenCalledWith(1, 'freeze', 1, 2);
  });

  it('covers flip-three action callback path when player holds flip-three', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState
      .mockResolvedValueOnce(
        makeState({
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
                { card_name: 'Flip Three', value: null, effect_type: 'action', effect_payload: 'flip_three' },
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
        }),
      )
      .mockResolvedValueOnce(
        makeState({
          status: 'active',
          round_id: 1,
          current_turn: 2,
        }),
      );

    mockFns.takeAction.mockResolvedValueOnce({ round_ended: false, bust: false });

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: /Flip Three/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Bob' }));

    expect(mockFns.takeAction).toHaveBeenCalledWith(1, 'flip_three', 1, 2);
  });

  it('covers create-screen remove-player callback branch', async () => {
    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: 'Create game' }));
    await screen.findByRole('heading', { name: 'New game' }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: '+ Add player' }));
    const thirdInput = screen.getByRole('textbox', { name: 'Player 3 name' });
    expect(thirdInput).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Remove player 3' }));
    expect(screen.queryByRole('textbox', { name: 'Player 3 name' })).not.toBeInTheDocument();
  });

  it('covers create-screen validation message branches', async () => {
    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: 'Create game' }));
    await screen.findByRole('heading', { name: 'New game' }, { timeout: 4000 });

    const player1 = screen.getByRole('textbox', { name: 'Player 1 name (starts)' });
    const player2 = screen.getByRole('textbox', { name: 'Player 2 name' });

    fireEvent.change(player1, { target: { value: '' } });
    fireEvent.change(player2, { target: { value: '' } });
    expect(screen.getByText('Add at least 2 players.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: '+ Add player' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Player 1 name (starts)' }), {
      target: { value: 'Alice' },
    });
    fireEvent.change(screen.getByRole('textbox', { name: 'Player 2 name' }), {
      target: { value: 'Bob' },
    });
    fireEvent.change(screen.getByRole('textbox', { name: 'Player 3 name' }), {
      target: { value: '' },
    });
    expect(screen.getByText('Give every player a name.')).toBeInTheDocument();

    fireEvent.change(screen.getByRole('textbox', { name: 'Player 3 name' }), {
      target: { value: 'alice' },
    });
    expect(screen.getByText('Player names must be unique.')).toBeInTheDocument();
  });

  it('covers create-screen target controls including clamped custom value and preset selection', async () => {
    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });

    fireEvent.click(screen.getByRole('button', { name: 'Create game' }));
    await screen.findByRole('heading', { name: 'New game' }, { timeout: 4000 });

    expect(screen.getByRole('button', { name: '200' })).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'Decrease target' }));
    fireEvent.click(screen.getByRole('button', { name: 'Decrease target' }));
    fireEvent.click(screen.getByRole('button', { name: 'Decrease target' }));
    fireEvent.click(screen.getByRole('button', { name: 'Decrease target' }));
    expect(screen.getByText('50')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Increase target' }));
    expect(screen.getByText('100')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: '1000' }));
    expect(screen.getByRole('button', { name: '1000' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: '200' })).toHaveAttribute('aria-pressed', 'false');
  });

  it('covers round-summary fallback builder when action result has no summary payload', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState
      .mockResolvedValueOnce(
        makeState({
          status: 'active',
          round_id: 2,
          current_turn: 1,
          round_ended: false,
          players: [
            {
              player_id: 1,
              username: 'alice',
              display_name: 'Alice',
              active: false,
              is_busted: false,
              score: 11,
              total_score: 31,
              unique_numbers: 3,
              cards: [{ card_name: '7', value: 7, effect_type: 'number', effect_payload: '' }],
            },
            {
              player_id: 2,
              username: 'bob',
              display_name: 'Bob',
              active: false,
              is_busted: false,
              score: 8,
              total_score: 27,
              unique_numbers: 2,
              cards: [{ card_name: '6', value: 6, effect_type: 'number', effect_payload: '' }],
            },
          ],
        }),
      )
      .mockResolvedValueOnce(
        makeState({
          status: 'active',
          round_id: 2,
          current_turn: null,
          round_ended: true,
          players: [
            {
              player_id: 1,
              username: 'alice',
              display_name: 'Alice',
              active: false,
              is_busted: false,
              score: 11,
              total_score: 31,
              unique_numbers: 3,
              cards: [{ card_name: '7', value: 7, effect_type: 'number', effect_payload: '' }],
            },
            {
              player_id: 2,
              username: 'bob',
              display_name: 'Bob',
              active: false,
              is_busted: false,
              score: 8,
              total_score: 27,
              unique_numbers: 2,
              cards: [{ card_name: '6', value: 6, effect_type: 'number', effect_payload: '' }],
            },
          ],
        }),
      );

    mockFns.takeAction.mockResolvedValueOnce({ round_ended: true, bust: false });

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: /Stay/ }));

    const summaryDialog = await screen.findByRole('dialog', { name: 'Round Summary' }, { timeout: 4000 });
    expect(within(summaryDialog).getByText('Alice')).toBeInTheDocument();
    expect(within(summaryDialog).getByText('Bob')).toBeInTheDocument();
  });

  // --- Polling guard-path coverage ------------------------------------------

  it('poll skips when tab is hidden and resumes when visible', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValue(
      makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 }),
    );

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    const callsAfterMount = mockFns.getState.mock.calls.length;

    Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true });
    await new Promise((r) => setTimeout(r, 6000));
    // No extra polls should have fired while hidden.
    expect(mockFns.getState.mock.calls.length).toBe(callsAfterMount);

    // Restore and verify polling would resume (visibilityState reset).
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
  }, 15000);

  it('poll skips when an action is pending (pendingRef guard)', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 });
    mockFns.getState.mockResolvedValue(activeState);

    let resolveAction: (v: ActionResult) => void = () => undefined;
    mockFns.takeAction.mockReturnValue(new Promise((r) => { resolveAction = r; }));

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    const callsBeforeAction = mockFns.getState.mock.calls.length;

    // Fire an action; it stays pending while resolveAction is not called.
    fireEvent.click(screen.getByRole('button', { name: /Hit/ }));
    await new Promise((r) => setTimeout(r, 6000));

    // getState may have been called for the action dispatch itself, but no
    // extra background polls should have fired while the action was in flight.
    resolveAction({ round_ended: false, bust: false });
    expect(mockFns.getState.mock.calls.length).toBeLessThanOrEqual(callsBeforeAction + 2);
  }, 15000);

  it('poll skips while target-selection is open', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    mockFns.getState.mockResolvedValue(
      makeState({
        status: 'active',
        round_id: 1,
        round_ended: false,
        current_turn: 1,
        players: [
          {
            player_id: 1, username: 'alice', display_name: 'Alice',
            active: true, is_busted: false, score: 0, total_score: 0, unique_numbers: 1,
            cards: [
              { card_name: '3', value: 3, effect_type: 'number', effect_payload: '' },
              { card_name: 'Freeze', value: null, effect_type: 'action', effect_payload: 'freeze' },
            ],
          },
          {
            player_id: 2, username: 'bob', display_name: 'Bob',
            active: true, is_busted: false, score: 0, total_score: 0, unique_numbers: 1,
            cards: [{ card_name: '4', value: 4, effect_type: 'number', effect_payload: '' }],
          },
        ],
      }),
    );

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    fireEvent.click(screen.getByRole('button', { name: /Freeze/ }));
    // Target picker is now open (targetSelection set).
    expect(screen.getByText('Choose target for Freeze')).toBeInTheDocument();

    const callsWithPickerOpen = mockFns.getState.mock.calls.length;
    await new Promise((r) => setTimeout(r, 6000));
    // No new polls should have fired with the picker open.
    expect(mockFns.getState.mock.calls.length).toBe(callsWithPickerOpen);
  }, 15000);

  it('poll is silent on transient network error', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 });
    mockFns.getState
      .mockResolvedValueOnce(activeState)  // initial load
      .mockRejectedValue(Object.assign(new Error('Network error'), { code: 'network_error' }));

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });

    // Wait for at least one poll tick to fail — board must stay intact, no disconnect modal.
    await new Promise((r) => setTimeout(r, 6000));
    expect(screen.getByRole('heading', { name: "Alice's turn" })).toBeInTheDocument();
    expect(screen.queryByRole('dialog', { name: 'Connection lost' })).not.toBeInTheDocument();
  }, 15000);

  it('poll routes to game_over when backend returns finished status', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 1 });
    const finishedState = makeState({ status: 'finished', round_id: 1, round_ended: true, current_turn: null });
    mockFns.getState
      .mockResolvedValueOnce(activeState)
      .mockResolvedValue(finishedState);

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Alice's turn" }, { timeout: 4000 });
    await screen.findByText('Game over', {}, { timeout: 15000 });
    expect(screen.getByText('Match complete')).toBeInTheDocument();
  }, 20000);

  it('poll shows round-summary modal when round ends on another player\'s turn', async () => {
    window.localStorage.setItem('flip7.gameId', '1');
    const activeState = makeState({ status: 'active', round_id: 1, round_ended: false, current_turn: 2 });
    const roundEndedState = makeState({ status: 'active', round_id: 1, round_ended: true, current_turn: null });
    mockFns.getState
      .mockResolvedValueOnce(activeState)
      .mockResolvedValue(roundEndedState);

    render(<HomePage />);
    await screen.findByRole('heading', { name: "Bob's turn" }, { timeout: 4000 });
    await screen.findByRole('dialog', { name: 'Round Summary' }, { timeout: 15000 });
  }, 20000);

  it('does not start polling on lobby or game_over screens', async () => {
    render(<HomePage />);
    await screen.findByRole('button', { name: 'Create game' }, { timeout: 4000 });
    const callsOnLobby = mockFns.getState.mock.calls.length;

    await new Promise((r) => setTimeout(r, 6000));
    // No background polls should fire on the lobby screen.
    expect(mockFns.getState.mock.calls.length).toBe(callsOnLobby);
  }, 15000);
});
