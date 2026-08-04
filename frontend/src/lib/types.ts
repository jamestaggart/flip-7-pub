// Shared types mapping backend responses into a frontend view model (requirements §7.2).

export type GameStatus = 'pending' | 'active' | 'finished' | 'abandoned';

export type CardEffectType = 'number' | 'modifier' | 'action' | string;

export interface Player {
  id: number;
  username: string;
  display_name?: string;
}

export interface GameSummary {
  id: number;
  game_code: string;
  status: GameStatus;
  target_score?: number;
  created_by?: number | null;
}

export interface RawCard {
  card_name: string;
  value?: number | null;
  effect_type: CardEffectType;
  effect_payload: string;
}

export interface RawStatePlayer {
  player_id: number;
  username: string;
  display_name?: string;
  active: boolean;
  is_busted: boolean;
  score: number;
  total_score: number;
  unique_numbers: number;
  cards: RawCard[];
}

export interface RawGameState {
  game_id: number;
  game_code: string;
  status: GameStatus;
  target_score: number;
  round_id?: number | null;
  round_ended?: boolean;
  active_player_count?: number;
  deck_remaining?: number;
  current_turn?: number | null;
  players: RawStatePlayer[];
}

export interface RoundSummaryEntry {
  player_id: number;
  username: string;
  display_name?: string;
  score: number;
  total_score: number | null;
}

export interface ActionResult {
  bust?: boolean;
  flip_seven?: boolean;
  second_chance_used?: boolean;
  round_ended?: boolean;
  deferred_action?: string;
  score?: number;
  round_summary?: RoundSummaryEntry[];
  outcome?: {
    round_ended?: boolean;
    round_summary?: RoundSummaryEntry[];
  };
  error?: string;
}

export interface GameResults {
  game_id: number;
  status: GameStatus;
  target_score: number;
  winner?: { player_id: number; username: string; display_name?: string; total_score: number } | null;
  standings: Array<{
    player_id: number;
    username: string;
    display_name?: string;
    seat_number: number | null;
    total_score: number;
    is_busted: boolean;
  }>;
}

// Presentation-only card families derived from backend fields (never rule logic).
export type CardFamily =
  | 'number'
  | 'modifier-positive'
  | 'multiplier'
  | 'modifier-negative'
  | 'freeze'
  | 'flip-three'
  | 'second-chance'
  | 'card-back';

export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'protected';

export type TurnActionKey = 'hit' | 'stay' | 'freeze' | 'flip_three';

export interface ApiError extends Error {
  code?: string;
  statusCode?: number;
  details?: unknown;
}
