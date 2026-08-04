// Centralized API client. All backend calls go through here (checklist §1).
import type {
  ActionResult,
  GameResults,
  GameSummary,
  Player,
  RawGameState,
  TurnActionKey,
  ApiError,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch {
    const error: ApiError = new Error('Network request failed. Check your connection and try again.');
    error.code = 'network_error';
    throw error;
  }

  const text = await res.text();
  let data: (Record<string, unknown> & { error?: string; detail?: string; error_code?: string; details?: unknown }) | null =
    null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    // Non-JSON response (e.g. a server HTML error page). Surface a clean message.
    const error: ApiError = new Error(
      res.ok ? 'The server returned an unexpected response.' : `Server error (${res.status}). Please try again.`,
    );
    error.code = res.ok ? 'invalid_response' : 'server_error';
    error.statusCode = res.status;
    throw error;
  }

  if (!res.ok) {
    const error: ApiError = new Error((data && (data.error || data.detail)) || `Request failed (${res.status})`);
    error.code = data?.error_code;
    error.statusCode = res.status;
    error.details = data?.details;
    throw error;
  }

  return data as T;
}

export const api = {
  listPlayers: () => request<Player[]>('/api/players/'),

  createPlayer: (username: string) =>
    request<Player>('/api/players/', {
      method: 'POST',
      body: JSON.stringify({ username, display_name: username }),
    }),

  updatePlayer: (playerId: number, displayName: string) =>
    request<Player>(`/api/players/${playerId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ display_name: displayName }),
    }),

  listGames: () => request<GameSummary[]>('/api/games/'),

  createGame: (createdBy: number | null, targetScore: number) =>
    request<GameSummary>('/api/games/create/', {
      method: 'POST',
      body: JSON.stringify({ created_by: createdBy, target_score: targetScore }),
    }),

  joinGame: (gameId: number, playerId: number, seatNumber: number) =>
    request<{ status: string; game_player_id: number }>(`/api/games/${gameId}/join/`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, seat_number: seatNumber }),
    }),

  removePlayer: (gameId: number, playerId: number) =>
    request<RawGameState>(`/api/games/${gameId}/remove_player/`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId }),
    }),

  startRound: (gameId: number) =>
    request<{ round_id: number; turn_id: number; state: RawGameState }>(`/api/games/${gameId}/start_round/`, {
      method: 'POST',
    }),

  getState: (gameId: number) => request<RawGameState>(`/api/games/${gameId}/state/`),

  closeGame: (gameId: number) =>
    request<null>(`/api/games/${gameId}/close/`, {
      method: 'POST',
    }),

  getResults: (gameId: number) => request<GameResults>(`/api/games/${gameId}/results/`),

  takeAction: (gameId: number, action: TurnActionKey, playerId: number, targetPlayerId?: number) =>
    request<ActionResult>(`/api/games/${gameId}/${action}/`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, target_player_id: targetPlayerId }),
    }),
};

export { API_BASE };
