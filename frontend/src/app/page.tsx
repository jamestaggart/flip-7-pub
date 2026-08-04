'use client';

// Flip 7 v2 — mobile-first state-machine screen router (checklist §1, §3-§14).
// The backend stays authoritative; this component only presents state and submits legal actions.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../lib/api';
import type {
  ApiError,
  GameResults,
  GameSummary,
  Player,
  RawGameState,
  RoundSummaryEntry,
  TurnActionKey,
} from '../lib/types';
import { feedbackForAction, roundSummaryFromResult, type BannerTone } from '../lib/presentation';
import { Button, PlayerPanel, Pill } from '../components/ui';
import { ConfirmLeaveModal, DisconnectModal, RoundSummaryModal, RulesModal } from '../components/modals';

type Screen = 'splash' | 'lobby' | 'create' | 'waiting' | 'active' | 'game_over';

interface CreateSettings {
  names: string[];
  targetScore: number;
}

const MIN_PLAYERS = 2;
const MAX_PLAYERS = 30;
const TARGET_PRESETS = [200, 300, 500, 750, 1000];
const MIN_TARGET = 50;
const MAX_TARGET = 2000;

const DEFAULT_SETTINGS: CreateSettings = {
  names: ['Player 1', 'Player 2'],
  targetScore: 200,
};

function displayName(player: { display_name?: string; username: string }): string {
  return player.display_name?.trim() || player.username;
}

function errorCode(error: unknown): string | undefined {
  return (error as ApiError)?.code;
}

function errorStatus(error: unknown): number | undefined {
  return (error as ApiError)?.statusCode;
}

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export default function HomePage() {
  const [screen, setScreen] = useState<Screen>('splash');
  const [players, setPlayers] = useState<Player[]>([]);
  const [games, setGames] = useState<GameSummary[]>([]);
  const [gamesLoading, setGamesLoading] = useState(true);
  const [gamesError, setGamesError] = useState<string | null>(null);

  const [gameId, setGameId] = useState<number | null>(null);
  const [state, setState] = useState<RawGameState | null>(null);
  const [results, setResults] = useState<GameResults | null>(null);

  const [settings, setSettings] = useState<CreateSettings>(DEFAULT_SETTINGS);
  const [banner, setBanner] = useState<{ headline: string; tone: BannerTone } | null>(null);
  const [roundSummary, setRoundSummary] = useState<RoundSummaryEntry[] | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [disconnected, setDisconnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);

  const [pending, setPending] = useState<string | null>(null);
  const [targetSelection, setTargetSelection] = useState<TurnActionKey | null>(null);
  const [justDrew, setJustDrew] = useState<number | null>(null);

  const [showRules, setShowRules] = useState(false);
  const [showConfirmLeave, setShowConfirmLeave] = useState(false);

  const drewTimer = useRef<number | null>(null);
  const pendingRef = useRef<string | null>(null);
  const attemptedRestoreRef = useRef(false);

  // --- Initial load (splash -> lobby) ---------------------------------------
  const loadLobby = useCallback(async () => {
    setGamesLoading(true);
    setGamesError(null);
    try {
      const [playerList, gameList] = await Promise.all([api.listPlayers(), api.listGames()]);
      setPlayers(playerList);
      setGames(gameList);
      setDisconnected(false);
    } catch (error) {
      if (errorCode(error) === 'network_error') setDisconnected(true);
      setGamesError(errorMessage(error, 'Unable to load games.'));
    } finally {
      setGamesLoading(false);
    }
  }, []);

  // FEAT-01: recover gracefully when the game we're in has been closed/deleted.
  const handleGameClosed = useCallback(() => {
    setGameId(null);
    setState(null);
    setResults(null);
    setRoundSummary(null);
    setBanner(null);
    setTargetSelection(null);
    setShowConfirmLeave(false);
    window.localStorage.removeItem('flip7.gameId');
    setToast('This game was closed.');
    setScreen('lobby');
    loadLobby();
  }, [loadLobby]);

  // --- Single-flight guard ---------------------------------------------------
  const runExclusive = useCallback(
    async (key: string, fn: () => Promise<void>) => {
      if (pendingRef.current) return;
      pendingRef.current = key;
      setPending(key);
      setToast(null);
      try {
        await fn();
      } catch (error) {
        if (errorCode(error) === 'network_error') {
          setDisconnected(true);
        } else if (errorStatus(error) === 404) {
          handleGameClosed();
        } else {
          setToast(errorMessage(error, 'Something went wrong. Try again.'));
        }
      } finally {
        pendingRef.current = null;
        setPending(null);
      }
    },
    [handleGameClosed],
  );

  const flashDrew = useCallback((playerId: number) => {
    setJustDrew(playerId);
    if (drewTimer.current) window.clearTimeout(drewTimer.current);
    drewTimer.current = window.setTimeout(() => setJustDrew(null), 400);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const start = Date.now();
    loadLobby().finally(() => {
      const elapsed = Date.now() - start;
      const wait = Math.max(0, 1200 - elapsed);
      window.setTimeout(() => {
        if (!cancelled) setScreen((current) => (current === 'splash' ? 'lobby' : current));
      }, wait);
    });
    return () => {
      cancelled = true;
      if (drewTimer.current) window.clearTimeout(drewTimer.current);
    };
  }, [loadLobby]);

  // --- Persistence for refresh/reconnect recovery ---------------------------
  useEffect(() => {
    if (gameId != null) window.localStorage.setItem('flip7.gameId', String(gameId));
  }, [gameId]);

  // FEAT-06: keep the active player in view for large rosters.
  useEffect(() => {
    if (screen !== 'active') return;
    const el = document.querySelector('.playerPanel[data-active="true"]');
    if (el instanceof HTMLElement && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [screen, state?.current_turn]);

  // --- State routing helper --------------------------------------------------
  const routeFromState = useCallback(async (next: RawGameState) => {
    setState(next);
    if (next.status === 'finished') {
      try {
        setResults(await api.getResults(next.game_id));
      } catch {
        /* results are best-effort */
      }
      setRoundSummary(null);
      setScreen('game_over');
    }
  }, []);

  const refreshState = useCallback(
    async (id: number) => {
      const next = await api.getState(id);
      await routeFromState(next);
      return next;
    },
    [routeFromState],
  );

  // --- Create game flow ------------------------------------------------------
  const resolvePlayer = useCallback(async (name: string, existing: Player[]): Promise<Player> => {
    const match = existing.find((p) => p.username.toLowerCase() === name.toLowerCase());
    if (match) return match;
    return api.createPlayer(name);
  }, []);

  const createGame = useCallback(
    (config: CreateSettings) =>
      runExclusive('create', async () => {
        const roster = await api.listPlayers();
        setPlayers(roster);
        const names = config.names.map((n) => n.trim()).filter((n) => n.length > 0);

        const resolved: Player[] = [];
        for (const name of names) {
          const player = await resolvePlayer(name, [...roster, ...resolved]);
          // FEAT-04: let players name their character once. Only set the display
          // name if this player hasn't been named yet, so we never re-prompt.
          if (!player.display_name?.trim() && name.toLowerCase() !== player.username.toLowerCase()) {
            try {
              await api.updatePlayer(player.id, name);
            } catch {
              /* naming is best-effort */
            }
          }
          resolved.push(player);
        }

        const [first, ...rest] = resolved;
        const game = await api.createGame(first.id, config.targetScore); // creator auto-joins seat 1
        let seat = 2;
        for (const player of rest) {
          await api.joinGame(game.id, player.id, seat);
          seat += 1;
        }

        setGameId(game.id);
        setSettings(config);
        const next = await api.getState(game.id);
        setState(next);
        setBanner(null);
        setRoundSummary(null);
        setResults(null);
        setScreen('waiting');
        await loadLobby();
      }),
    [runExclusive, resolvePlayer, loadLobby],
  );

  // --- Open / join an existing game from the lobby --------------------------
  const openGame = useCallback(
    (id: number) =>
      runExclusive(`open-${id}`, async () => {
        const next = await api.getState(id);
        setGameId(id);
        setState(next);
        setBanner(null);
        setRoundSummary(null);
        if (next.status === 'finished') {
          setResults(await api.getResults(id));
          setScreen('game_over');
        } else if (next.round_id && !next.round_ended) {
          setScreen('active');
        } else {
          setScreen('waiting');
        }
      }),
    [runExclusive],
  );

  // FEAT-36: restore the last-opened game after a full page refresh.
  useEffect(() => {
    if (screen !== 'lobby') return;
    if (gameId != null) return;
    if (attemptedRestoreRef.current) return;

    attemptedRestoreRef.current = true;
    const raw = window.localStorage.getItem('flip7.gameId');
    if (!raw) return;

    const persistedId = Number(raw);
    if (!Number.isInteger(persistedId) || persistedId <= 0) {
      window.localStorage.removeItem('flip7.gameId');
      return;
    }

    void openGame(persistedId);
  }, [screen, gameId, openGame]);

  // --- Start / next round ----------------------------------------------------
  const startRound = useCallback(
    () =>
      runExclusive('start', async () => {
        if (gameId == null) return;
        const res = await api.startRound(gameId);
        setState(res.state);
        setRoundSummary(null);
        setBanner(null);
        setScreen('active');
      }),
    [runExclusive, gameId],
  );

  // FEAT-05: remove a player from the waiting room before the round starts.
  const removePlayer = useCallback(
    (playerId: number) =>
      runExclusive(`remove-${playerId}`, async () => {
        if (gameId == null) return;
        const next = await api.removePlayer(gameId, playerId);
        setState(next);
      }),
    [runExclusive, gameId],
  );

  // --- Turn actions ----------------------------------------------------------
  const submitAction = useCallback(
    (action: TurnActionKey, targetPlayerId?: number) =>
      runExclusive(`action-${action}`, async () => {
        if (gameId == null || !state) return;
        const actingId = state.current_turn;
        if (!actingId) {
          setToast('No active player for this action.');
          return;
        }
        const result = await api.takeAction(gameId, action, actingId, targetPlayerId);
        setTargetSelection(null);

        const next = await refreshState(gameId);
        setBanner(feedbackForAction(result, action));

        if (action === 'hit' && !result.bust) flashDrew(actingId);

        const roundEnded = Boolean(result.round_ended || result.outcome?.round_ended);
        if (roundEnded && next.status !== 'finished') {
          const summary = roundSummaryFromResult(result) ?? buildSummaryFromState(next);
          setRoundSummary(summary);
        }
      }),
    [runExclusive, gameId, state, refreshState, flashDrew],
  );

  const beginAction = useCallback(
    (action: TurnActionKey) => {
      if (action === 'freeze' || action === 'flip_three') {
        setTargetSelection(action);
        return;
      }
      submitAction(action);
    },
    [submitAction],
  );

  // --- Leave / reset ---------------------------------------------------------
  const leaveGame = useCallback(() => {
    setShowConfirmLeave(false);
    setGameId(null);
    setState(null);
    setResults(null);
    setRoundSummary(null);
    setBanner(null);
    window.localStorage.removeItem('flip7.gameId');
    loadLobby();
    setScreen('lobby');
  }, [loadLobby]);

  // FEAT-01: any player can permanently close (delete) the game for everyone.
  const closeGame = useCallback(
    () =>
      runExclusive('close', async () => {
        if (gameId != null) {
          try {
            await api.closeGame(gameId);
          } catch (error) {
            // A 404 means it's already gone — treat as success.
            if (errorStatus(error) !== 404) throw error;
          }
        }
        setShowConfirmLeave(false);
        setGameId(null);
        setState(null);
        setResults(null);
        setRoundSummary(null);
        setBanner(null);
        setTargetSelection(null);
        window.localStorage.removeItem('flip7.gameId');
        setScreen('lobby');
        await loadLobby();
      }),
    [runExclusive, gameId, loadLobby],
  );

  const reconnect = useCallback(async () => {
    setReconnecting(true);
    try {
      if (gameId != null && screen !== 'lobby' && screen !== 'splash') {
        await refreshState(gameId);
      } else {
        await loadLobby();
      }
      setDisconnected(false);
    } catch {
      /* stay disconnected */
    } finally {
      setReconnecting(false);
    }
  }, [gameId, screen, refreshState, loadLobby]);

  const playAgain = useCallback(() => createGame(settings), [createGame, settings]);

  // --- Derived board data ----------------------------------------------------
  const activePlayer = useMemo(
    () => state?.players.find((p) => p.player_id === state?.current_turn) ?? null,
    [state],
  );

  const currentHolds = useCallback(
    (payload: string) => activePlayer?.cards.some((card) => card.effect_payload === payload) ?? false,
    [activePlayer],
  );

  const roundActive = Boolean(state?.round_id && !state?.round_ended && state?.status !== 'finished');

  // ==========================================================================
  // Render
  // ==========================================================================
  const modals = (
    <>
      {showRules && <RulesModal onClose={() => setShowRules(false)} />}
      {showConfirmLeave && (
        <ConfirmLeaveModal
          onCancel={() => setShowConfirmLeave(false)}
          onLeave={closeGame}
          loading={pending === 'close'}
        />
      )}
      {roundSummary && state && (
        <RoundSummaryModal
          summary={roundSummary}
          targetScore={state.target_score}
          loading={pending === 'start'}
          onNextRound={startRound}
        />
      )}
      {disconnected && <DisconnectModal onRetry={reconnect} retrying={reconnecting} />}
    </>
  );

  if (screen === 'splash') {
    return (
      <main className="appViewport">
        <div className="splash">
          <div className="splashInner">
            <div className="brandLogo">FLIP 7</div>
            <p className="loadingText">Shuffling the deck…</p>
            <span className="btnSpinner" aria-hidden="true" style={{ width: 24, height: 24 }} />
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="appViewport">
      <div className={`screen ${screen === 'active' ? 'board' : ''}`}>
        {toast && (
          <div className="errorToast" role="alert">
            <span>{toast}</span>
            <button type="button" className="closeBtn" aria-label="Dismiss" onClick={() => setToast(null)}>
              ✕
            </button>
          </div>
        )}

        {screen === 'lobby' &&
          renderLobby({
            games,
            gamesLoading,
            gamesError,
            pending,
            onCreate: () => {
              setSettings(DEFAULT_SETTINGS);
              setScreen('create');
            },
            onRefresh: loadLobby,
            onOpen: openGame,
            onRules: () => setShowRules(true),
          })}

        {screen === 'create' &&
          renderCreate({
            settings,
            setSettings,
            pending: pending === 'create',
            onBack: () => setScreen('lobby'),
            onCreate: createGame,
          })}

        {screen === 'waiting' &&
          state &&
          renderWaiting({
            state,
            pending: pending === 'start',
            removingId: pending?.startsWith('remove-') ? Number(pending.slice('remove-'.length)) : null,
            onStart: startRound,
            onRemovePlayer: removePlayer,
            onLeave: () => setShowConfirmLeave(true),
            onRules: () => setShowRules(true),
          })}

        {screen === 'active' &&
          state &&
          renderBoard({
            state,
            activePlayer,
            banner,
            justDrew,
            roundActive,
            pending,
            targetSelection,
            currentHolds,
            onAction: beginAction,
            onConfirmTarget: (action, targetPlayerId) => submitAction(action, targetPlayerId),
            onCancelTarget: () => setTargetSelection(null),
            onRules: () => setShowRules(true),
            onLeave: () => setShowConfirmLeave(true),
          })}

        {screen === 'game_over' &&
          renderGameOver({
            results,
            state,
            pending: pending === 'create',
            onPlayAgain: playAgain,
            onNewGame: leaveGame,
          })}
      </div>
      {modals}
    </main>
  );
}

// ============================================================================
// Screen render functions
// ============================================================================

function buildSummaryFromState(state: RawGameState): RoundSummaryEntry[] {
  return state.players.map((p) => ({
    player_id: p.player_id,
    username: p.username,
    display_name: p.display_name,
    score: p.score,
    total_score: p.total_score,
  }));
}

function renderLobby(props: {
  games: GameSummary[];
  gamesLoading: boolean;
  gamesError: string | null;
  pending: string | null;
  onCreate: () => void;
  onRefresh: () => void;
  onOpen: (id: number) => void;
  onRules: () => void;
}) {
  const joinable = props.games.filter((g) => g.status !== 'finished' && g.status !== 'abandoned');
  return (
    <>
      <div className="centerText" style={{ marginTop: 'var(--space-5)' }}>
        <div className="brandLogo">FLIP 7</div>
        <p className="muted">Press-your-luck, pass-and-play.</p>
      </div>

      <div className="stackGap">
        <Button variant="primary" block onClick={props.onCreate}>
          Create game
        </Button>
        <Button variant="ghost" block onClick={props.onRules}>
          How to play
        </Button>
      </div>

      <div className="feltPanel">
        <div className="rowBetween" style={{ marginBottom: 'var(--space-3)' }}>
          <h2 className="sectionTitle">Open games</h2>
          <Button small variant="ghost" onClick={props.onRefresh} loading={props.gamesLoading}>
            Refresh
          </Button>
        </div>

        {props.gamesLoading ? (
          <p className="muted">Loading games…</p>
        ) : props.gamesError ? (
          <div className="emptyState" style={{ color: 'var(--text-muted)', borderColor: 'rgba(255,255,255,0.2)' }}>
            {props.gamesError}
          </div>
        ) : joinable.length === 0 ? (
          <div className="emptyState" style={{ color: 'var(--text-muted)', borderColor: 'rgba(255,255,255,0.2)' }}>
            No open games yet. Create one to get started.
          </div>
        ) : (
          <div className="stackGap">
            {joinable.map((game) => (
              <div key={game.id} className="lobbyRow">
                <div className="lobbyRowMeta">
                  <strong>Game {game.game_code}</strong>
                  <span>Status: {game.status}</span>
                </div>
                <Button
                  small
                  variant="secondary"
                  loading={props.pending === `open-${game.id}`}
                  onClick={() => props.onOpen(game.id)}
                >
                  Open
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function renderCreate(props: {
  settings: CreateSettings;
  setSettings: React.Dispatch<React.SetStateAction<CreateSettings>>;
  pending: boolean;
  onBack: () => void;
  onCreate: (config: CreateSettings) => void;
}) {
  const { settings } = props;
  const trimmed = settings.names.map((n) => n.trim());
  const filled = trimmed.filter((n) => n.length > 0);
  const lowerNames = filled.map((n) => n.toLowerCase());
  const hasDuplicate = new Set(lowerNames).size !== lowerNames.length;
  const enoughPlayers = filled.length >= MIN_PLAYERS;
  const allNamed = trimmed.every((n) => n.length > 0);
  const namesValid = enoughPlayers && allNamed && !hasDuplicate;
  const targetValid = settings.targetScore >= MIN_TARGET && settings.targetScore <= MAX_TARGET;
  const valid = namesValid && targetValid;

  const setTarget = (value: number) =>
    props.setSettings((prev) => ({ ...prev, targetScore: Math.min(MAX_TARGET, Math.max(MIN_TARGET, value)) }));

  const setName = (index: number, value: string) =>
    props.setSettings((prev) => {
      const names = [...prev.names];
      names[index] = value;
      return { ...prev, names };
    });

  const addPlayer = () =>
    props.setSettings((prev) =>
      prev.names.length >= MAX_PLAYERS
        ? prev
        : { ...prev, names: [...prev.names, `Player ${prev.names.length + 1}`] },
    );

  const removePlayer = (index: number) =>
    props.setSettings((prev) =>
      prev.names.length <= MIN_PLAYERS
        ? prev
        : { ...prev, names: prev.names.filter((_, i) => i !== index) },
    );

  return (
    <>
      <div className="rowBetween">
        <button type="button" className="iconBtn" aria-label="Back to lobby" onClick={props.onBack}>
          ←
        </button>
        <h1 className="sectionTitle" style={{ color: 'var(--text-on-felt)' }}>
          New game
        </h1>
        <span style={{ width: 40 }} />
      </div>

      <div className="paperPanel">
        <div className="rowBetween" style={{ marginBottom: 'var(--space-2)' }}>
          <label style={{ margin: 0 }}>Players ({settings.names.length}/{MAX_PLAYERS})</label>
          <Button
            small
            variant="secondary"
            disabled={settings.names.length >= MAX_PLAYERS}
            onClick={addPlayer}
          >
            + Add player
          </Button>
        </div>

        <div className="playerInputList">
          {settings.names.map((name, index) => (
            <div key={index} className="field" style={{ marginBottom: 0 }}>
              <label htmlFor={`p${index}`}>Player {index + 1} name{index === 0 ? ' (starts)' : ''}</label>
              <div className="rowBetween" style={{ gap: 'var(--space-2)' }}>
                <input
                  id={`p${index}`}
                  className="input"
                  style={{ flex: 1 }}
                  value={name}
                  maxLength={20}
                  onChange={(e) => setName(index, e.target.value)}
                />
                {settings.names.length > MIN_PLAYERS && (
                  <button
                    type="button"
                    className="iconBtn"
                    aria-label={`Remove player ${index + 1}`}
                    onClick={() => removePlayer(index)}
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {!namesValid && (
          <p className="uniqueProgress" style={{ color: 'var(--coral)' }}>
            {!enoughPlayers
              ? `Add at least ${MIN_PLAYERS} players.`
              : !allNamed
                ? 'Give every player a name.'
                : 'Player names must be unique.'}
          </p>
        )}

        <div className="field">
          <label>Target score</label>
          <div className="stepper">
            <button
              type="button"
              className="btn secondary stepBtn"
              aria-label="Decrease target"
              onClick={() => setTarget(settings.targetScore - 50)}
            >
              −
            </button>
            <span className="stepValue">{settings.targetScore}</span>
            <button
              type="button"
              className="btn secondary stepBtn"
              aria-label="Increase target"
              onClick={() => setTarget(settings.targetScore + 50)}
            >
              +
            </button>
          </div>
          <div className="presetRow">
            {TARGET_PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                className={`presetBtn ${settings.targetScore === preset ? 'selected' : ''}`}
                aria-pressed={settings.targetScore === preset}
                onClick={() => setTarget(preset)}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

        <Button
          variant="primary"
          block
          disabled={!valid}
          loading={props.pending}
          onClick={() => props.onCreate(settings)}
        >
          Create &amp; continue
        </Button>
      </div>
    </>
  );
}

function renderWaiting(props: {
  state: RawGameState;
  pending: boolean;
  removingId: number | null;
  onStart: () => void;
  onRemovePlayer: (playerId: number) => void;
  onLeave: () => void;
  onRules: () => void;
}) {
  const { state } = props;
  const ready = state.players.length >= MIN_PLAYERS;
  const canRemove = state.players.length > MIN_PLAYERS;
  return (
    <>
      <div className="gameHeader">
        <button type="button" className="iconBtn" aria-label="Close game" onClick={props.onLeave}>
          ←
        </button>
        <div className="headerStat">
          <span className="statLabel">Game</span>
          <span className="statValue">{state.game_code}</span>
        </div>
        <button type="button" className="iconBtn" aria-label="How to play" onClick={props.onRules}>
          ?
        </button>
      </div>

      <div className="feltPanel">
        <h2 className="sectionTitle">Waiting room</h2>
        <p className="muted" style={{ marginTop: 4 }}>
          Target score {state.target_score}. {state.players.length} players ready. The first player starts.
        </p>
        <div className="rosterGrid" style={{ marginTop: 'var(--space-4)' }}>
          {state.players.map((player, index) => (
            <div key={player.player_id} className="rosterRow">
              <span className="rosterName">
                <span className={`avatar ${index === 0 ? '' : 'p2'}`} aria-hidden="true">
                  {displayName(player).charAt(0).toUpperCase()}
                </span>
                {displayName(player)}
              </span>
              {canRemove ? (
                <button
                  type="button"
                  className="iconBtn"
                  aria-label={`Remove ${displayName(player)}`}
                  disabled={props.removingId != null}
                  onClick={() => props.onRemovePlayer(player.player_id)}
                >
                  {props.removingId === player.player_id ? <span className="btnSpinner" /> : '✕'}
                </button>
              ) : (
                <Pill tone="ready">Ready</Pill>
              )}
            </div>
          ))}
        </div>
      </div>

      <Button variant="primary" block disabled={!ready} loading={props.pending} onClick={props.onStart}>
        Start game
      </Button>
      <Button variant="ghost" block onClick={props.onLeave}>
        Close game
      </Button>
    </>
  );
}

function renderBoard(props: {
  state: RawGameState;
  activePlayer: RawGameState['players'][number] | null;
  banner: { headline: string; tone: BannerTone } | null;
  justDrew: number | null;
  roundActive: boolean;
  pending: string | null;
  targetSelection: TurnActionKey | null;
  currentHolds: (payload: string) => boolean;
  onAction: (action: TurnActionKey) => void;
  onConfirmTarget: (action: TurnActionKey, targetPlayerId: number) => void;
  onCancelTarget: () => void;
  onRules: () => void;
  onLeave: () => void;
}) {
  const { state, activePlayer } = props;
  // FEAT-03: render players in stable seat order; the active player is shown via
  // the isActive highlight only, never by re-sorting the board.
  const players = state.players;
  // FEAT-02: Freeze / Flip Three can target any active player in the roster.
  const activeTargets = players.filter((p) => p.active);
  const actionsDisabled = Boolean(props.pending) || !props.roundActive || props.targetSelection != null;

  return (
    <>
      <div className="gameHeader">
        <button type="button" className="iconBtn" aria-label="Close game" onClick={props.onLeave}>
          ☰
        </button>
        <div className="headerStat">
          <span className="statLabel">Target</span>
          <span className="statValue">{state.target_score}</span>
        </div>
        <div className="headerStat">
          <span className="statLabel">Deck</span>
          <span className="statValue">{state.deck_remaining ?? '—'}</span>
        </div>
        <button type="button" className="iconBtn" aria-label="How to play" onClick={props.onRules}>
          ?
        </button>
      </div>

      <div className="turnBanner" aria-live="polite">
        <h2>{activePlayer ? `${displayName(activePlayer)}'s turn` : 'Round complete'}</h2>
        <p>{props.banner ? props.banner.headline : 'Hit to draw or Stay to bank your score.'}</p>
      </div>

      {props.banner && (
        <div className={`resultBanner ${props.banner.tone}`} role="status">
          {props.banner.headline}
        </div>
      )}

      <div className="playersStack">
        {players.map((player) => (
          <PlayerPanel
            key={player.player_id}
            player={player}
            isActive={player.player_id === state.current_turn}
            isBust={player.is_busted}
            targetScore={state.target_score}
            justDrew={props.justDrew === player.player_id}
          />
        ))}
      </div>

      {props.targetSelection ? (
        <div className="feltPanel" aria-live="assertive">
          <h2 className="sectionTitle">
            Choose target for {props.targetSelection === 'freeze' ? 'Freeze' : 'Flip Three'}
          </h2>
          {activeTargets.length === 0 ? (
            <p className="muted" style={{ margin: '4px 0 var(--space-3)' }}>
              No legal target available.
            </p>
          ) : (
            <div className="stackGap" style={{ marginBottom: 'var(--space-3)' }}>
              {activeTargets.map((target) => (
                <Button
                  key={target.player_id}
                  variant="danger"
                  block
                  loading={props.pending === `action-${props.targetSelection}`}
                  onClick={() =>
                    props.targetSelection && props.onConfirmTarget(props.targetSelection, target.player_id)
                  }
                >
                  {displayName(target)}
                  {target.player_id === props.activePlayer?.player_id ? ' (yourself)' : ''}
                </Button>
              ))}
            </div>
          )}
          <Button variant="ghost" block onClick={props.onCancelTarget}>
            Cancel
          </Button>
        </div>
      ) : (
        <div className="actionPanel">
          <button
            type="button"
            className="btn actionBtn hit"
            disabled={actionsDisabled}
            onClick={() => props.onAction('hit')}
          >
            {props.pending === 'action-hit' ? <span className="btnSpinner" /> : '＋'}
            Hit
            <small>Draw a card</small>
          </button>
          <button
            type="button"
            className="btn actionBtn stay"
            disabled={actionsDisabled || (activePlayer?.cards.length ?? 0) === 0}
            onClick={() => props.onAction('stay')}
          >
            {props.pending === 'action-stay' ? <span className="btnSpinner" /> : '✓'}
            Stay
            <small>Bank the round</small>
          </button>
          {props.currentHolds('freeze') && (
            <button
              type="button"
              className="btn actionBtn freeze"
              disabled={actionsDisabled}
              onClick={() => props.onAction('freeze')}
            >
              ❄ Freeze
              <small>Stop a player</small>
            </button>
          )}
          {props.currentHolds('flip_three') && (
            <button
              type="button"
              className="btn actionBtn flip_three"
              disabled={actionsDisabled}
              onClick={() => props.onAction('flip_three')}
            >
              ◫ Flip Three
              <small>Force 3 draws</small>
            </button>
          )}
        </div>
      )}
    </>
  );
}

function renderGameOver(props: {
  results: GameResults | null;
  state: RawGameState | null;
  pending: boolean;
  onPlayAgain: () => void;
  onNewGame: () => void;
}) {
  const { results } = props;
  const standings = results?.standings ?? [];
  const winner = results?.winner ?? standings[0] ?? null;
  const targetScore = results?.target_score ?? props.state?.target_score ?? 0;

  return (
    <>
      <div className="paperPanel">
        <div className="winnerBurst">
          <div className="goTitle">Game over</div>
          <div className="goWinner">{winner ? `${winner.display_name?.trim() || winner.username} wins!` : 'Match complete'}</div>
          <p className="muted">First to {targetScore} points.</p>
        </div>

        <div className="standingsList">
          {standings.map((row, index) => (
            <div key={row.player_id} className="standingRow">
              <span className="rank">{index + 1}</span>
              <span className="playerName" style={{ fontSize: '1rem' }}>
                {row.display_name?.trim() || row.username}
              </span>
              <span className="finalScore">{row.total_score}</span>
            </div>
          ))}
        </div>

        <div className="stackGap">
          <Button variant="primary" block loading={props.pending} onClick={props.onPlayAgain}>
            Play again (same settings)
          </Button>
          <Button variant="ghost" block onClick={props.onNewGame}>
            New game
          </Button>
        </div>
      </div>
    </>
  );
}
