'use client';

// Presentational UI primitives for the v2 redesign (checklist §2). Prop-driven, no game logic.
import { useEffect, useRef, type ReactNode } from 'react';
import type { RawCard, RawStatePlayer, RiskLevel } from '../lib/types';
import { cardFamily, cardLabel, hasSecondChance, riskLabel, riskLevel } from '../lib/presentation';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'success' | 'danger';

export function Button({
  children,
  variant = 'secondary',
  block,
  small,
  loading,
  disabled,
  onClick,
  type = 'button',
  className,
  ...rest
}: {
  children: ReactNode;
  variant?: ButtonVariant;
  block?: boolean;
  small?: boolean;
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit';
  className?: string;
} & Record<string, unknown>) {
  const classes = ['btn', variant, block ? 'block' : '', small ? 'small' : '', className || '']
    .filter(Boolean)
    .join(' ');
  return (
    <button type={type} className={classes} disabled={disabled || loading} onClick={onClick} {...rest}>
      {loading && <span className="btnSpinner" aria-hidden="true" />}
      {children}
    </button>
  );
}

export function Spinner() {
  return <span className="btnSpinner" aria-hidden="true" />;
}

export function Pill({ tone, children }: { tone: 'ready' | 'active' | 'waiting' | 'neutral'; children: ReactNode }) {
  return (
    <span className={`pill ${tone}`}>
      <span className="dot" aria-hidden="true" />
      {children}
    </span>
  );
}

export function Modal({
  title,
  onClose,
  dismissible = true,
  children,
  footer,
  labelledBy = 'modal-title',
}: {
  title: string;
  onClose?: () => void;
  dismissible?: boolean;
  children: ReactNode;
  footer?: ReactNode;
  labelledBy?: string;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const dialog = dialogRef.current;
    const selector =
      'button:not([disabled]), [href], input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

    const focusables = () =>
      Array.from(dialog?.querySelectorAll<HTMLElement>(selector) ?? []).filter((el) => !el.hasAttribute('disabled'));

    const timer = window.setTimeout(() => (focusables()[0] ?? dialog)?.focus(), 0);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && dismissible && onClose) {
        onClose();
        return;
      }
      if (event.key !== 'Tab') return;
      const items = focusables();
      if (items.length === 0) {
        event.preventDefault();
        return;
      }
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener('keydown', onKeyDown);
      previouslyFocused?.focus?.();
    };
  }, [dismissible, onClose]);

  return (
    <div
      className="overlay"
      role="presentation"
      onClick={dismissible && onClose ? onClose : undefined}
    >
      <div
        ref={dialogRef}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modalHeader">
          <h2 className="modalTitle" id={labelledBy}>
            {title}
          </h2>
          {dismissible && onClose && (
            <button type="button" className="closeBtn" aria-label="Close dialog" onClick={onClose}>
              ✕
            </button>
          )}
        </div>
        {children}
        {footer && <div className="stackGap" style={{ marginTop: 'var(--space-4)' }}>{footer}</div>}
      </div>
    </div>
  );
}

export function GameCard({ card, newlyDrawn }: { card: RawCard; newlyDrawn?: boolean }) {
  const family = cardFamily(card);
  const classes = ['gameCard', family, newlyDrawn ? 'newlyDrawn' : ''].filter(Boolean).join(' ');
  return (
    <div className={classes} title={card.card_name}>
      {cardLabel(card)}
    </div>
  );
}

export function CardRow({ cards, highlightLast }: { cards: RawCard[]; highlightLast?: boolean }) {
  if (cards.length === 0) {
    return <p className="uniqueProgress">No cards drawn yet.</p>;
  }
  return (
    <div className="cardRow" aria-label={`${cards.length} cards`}>
      {cards.map((card, index) => (
        <GameCard
          key={`${card.card_name}-${index}`}
          card={card}
          newlyDrawn={highlightLast && index === cards.length - 1}
        />
      ))}
    </div>
  );
}

export function RiskMeter({ level }: { level: RiskLevel }) {
  const filled = level === 'high' ? 3 : level === 'medium' ? 2 : level === 'low' || level === 'protected' ? 1 : 0;
  const colorClass = level === 'high' ? 'high' : level === 'medium' ? 'medium' : 'low';
  const textClass = level === 'protected' ? 'protected' : colorClass;
  return (
    <div className="riskMeter">
      <div className="riskDots" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <i key={i} className={i < filled ? `on ${colorClass}` : ''} />
        ))}
      </div>
      <span className={`riskText ${textClass}`}>{riskLabel(level)}</span>
    </div>
  );
}

export function PlayerPanel({
  player,
  isActive,
  isBust,
  targetScore,
  justDrew,
}: {
  player: RawStatePlayer;
  isActive: boolean;
  isBust: boolean;
  targetScore: number;
  justDrew: boolean;
}) {
  const protectedByChance = hasSecondChance(player.cards);
  const level = riskLevel(player.unique_numbers, player.cards.length, protectedByChance);
  const classes = ['playerPanel', isActive ? 'isActive' : '', isBust ? 'isBust' : ''].filter(Boolean).join(' ');
  const name = player.display_name?.trim() || player.username;
  const initial = name.charAt(0).toUpperCase();

  return (
    <section className={classes} data-active={isActive ? 'true' : undefined} aria-label={`${name} panel`}>
      <div className="playerTop">
        <div className="playerIdentity">
          <span className={`avatar ${isActive ? '' : 'p2'}`} aria-hidden="true">
            {initial}
          </span>
          <span className="playerName">{name}</span>
        </div>
        {isBust ? (
          <Pill tone="waiting">Bust</Pill>
        ) : isActive ? (
          <Pill tone="active">Your turn</Pill>
        ) : (
          <Pill tone="neutral">Waiting</Pill>
        )}
      </div>

      <div className="scoreRow">
        <div className="scoreBox">
          <span className="scoreLabel">Round</span>
          <span className="scoreValue">{player.score}</span>
        </div>
        <div className="scoreBox">
          <span className="scoreLabel">Total / {targetScore}</span>
          <span className="scoreValue">{player.total_score}</span>
        </div>
        <RiskMeter level={level} />
      </div>

      <CardRow cards={player.cards} highlightLast={justDrew} />
      <p className="uniqueProgress">Unique numbers: {player.unique_numbers} / 7</p>

      {level === 'high' && !protectedByChance && (
        <div className="dupWarning">
          <span aria-hidden="true">⚠</span> Duplicate danger — one repeat number busts this run.
        </div>
      )}
    </section>
  );
}
