'use client';

// Modal dialogs for the v2 redesign (checklist §12, §14).
import type { RoundSummaryEntry } from '../lib/types';
import { Button, Modal } from './ui';

export function RulesModal({ onClose }: { onClose: () => void }) {
  const rules: Array<{ term: string; text: string }> = [
    { term: 'Hit', text: 'Draw another card to grow your round score.' },
    { term: 'Stay', text: 'Bank your current round score and end your run safely.' },
    { term: 'Duplicate / Bust', text: 'Drawing a number you already have busts the run and scores 0 for the round.' },
    { term: 'Flip 7', text: 'Collect seven unique numbers for a big bonus and instant round end.' },
    { term: 'Freeze', text: 'Force a target player to stop and bank their current run.' },
    { term: 'Flip Three', text: 'Make a target draw three cards in a row.' },
    { term: 'Second Chance', text: 'Automatically cancels the next bust once, then is discarded.' },
  ];
  return (
    <Modal title="How to Play" onClose={onClose} labelledBy="rules-title">
      <ul className="rulesList">
        {rules.map((rule) => (
          <li key={rule.term}>
            <strong>{rule.term}:</strong> {rule.text}
          </li>
        ))}
      </ul>
      <div style={{ marginTop: 'var(--space-4)' }}>
        <Button variant="primary" block onClick={onClose}>
          Got it
        </Button>
      </div>
    </Modal>
  );
}

export function ConfirmLeaveModal({
  onCancel,
  onLeave,
  loading,
}: {
  onCancel: () => void;
  onLeave: () => void;
  loading?: boolean;
}) {
  return (
    <Modal title="Close game?" onClose={onCancel} labelledBy="leave-title">
      <p>This permanently deletes the game and all its progress for everyone. This can&apos;t be undone.</p>
      <div className="stackGap" style={{ marginTop: 'var(--space-4)' }}>
        <Button variant="danger" block loading={loading} onClick={onLeave}>
          Close game
        </Button>
        <Button variant="ghost" block onClick={onCancel}>
          Keep playing
        </Button>
      </div>
    </Modal>
  );
}

export function DisconnectModal({ onRetry, retrying }: { onRetry: () => void; retrying: boolean }) {
  return (
    <Modal title="Connection lost" dismissible={false} labelledBy="disconnect-title">
      <p>We lost contact with the game server. Your last board is preserved. Reconnect to continue.</p>
      <div style={{ marginTop: 'var(--space-4)' }}>
        <Button variant="primary" block loading={retrying} onClick={onRetry}>
          {retrying ? 'Reconnecting…' : 'Reconnect'}
        </Button>
      </div>
    </Modal>
  );
}

export function RoundSummaryModal({
  summary,
  targetScore,
  onNextRound,
  loading,
}: {
  summary: RoundSummaryEntry[];
  targetScore: number;
  onNextRound: () => void;
  loading: boolean;
}) {
  const topScore = Math.max(...summary.map((entry) => entry.score), 0);
  return (
    <Modal title="Round Summary" dismissible={false} labelledBy="summary-title">
      <div className="summaryGrid">
        {summary.map((entry) => {
          const isWinner = entry.score > 0 && entry.score === topScore;
          return (
            <div key={entry.player_id} className={`summaryCard ${isWinner ? 'winner' : ''}`}>
              <div>
                <div className="playerName">{entry.display_name?.trim() || entry.username}</div>
                <div className="summaryOutcome">
                  {entry.score > 0 ? 'Banked this round' : 'No points this round'}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="summaryScore">+{entry.score}</div>
                <div className="summaryOutcome">Total {entry.total_score ?? '—'} / {targetScore}</div>
              </div>
            </div>
          );
        })}
      </div>
      <Button variant="primary" block loading={loading} onClick={onNextRound}>
        {loading ? 'Dealing…' : 'Next round'}
      </Button>
    </Modal>
  );
}
