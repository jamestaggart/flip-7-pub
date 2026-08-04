// Presentation-only derivations from backend state. No game-rule logic here.
import type { ActionResult, CardFamily, RawCard, RiskLevel, TurnActionKey } from './types';

export function cardFamily(card: RawCard): CardFamily {
  if (card.effect_type === 'number') return 'number';
  if (card.effect_payload === 'freeze') return 'freeze';
  if (card.effect_payload === 'flip_three') return 'flip-three';
  if (card.effect_payload === 'second_chance') return 'second-chance';
  if (card.effect_type === 'modifier') {
    if (typeof card.value === 'number' && card.value < 0) return 'modifier-negative';
    if (card.card_name.toLowerCase().includes('x') || card.effect_payload === 'multiplier') return 'multiplier';
    return 'modifier-positive';
  }
  return 'number';
}

export function cardLabel(card: RawCard): string {
  if (card.effect_type === 'number') return String(card.value ?? card.card_name);
  if (card.effect_payload === 'freeze') return 'Freeze';
  if (card.effect_payload === 'flip_three') return 'Flip 3';
  if (card.effect_payload === 'second_chance') return '2nd';
  return card.card_name;
}

export function hasSecondChance(cards: RawCard[]): boolean {
  return cards.some((card) => card.effect_payload === 'second_chance');
}

export function riskLevel(uniqueNumbers: number, cardCount: number, protectedBySecondChance: boolean): RiskLevel {
  if (cardCount === 0) return 'none';
  if (protectedBySecondChance) return 'protected';
  if (uniqueNumbers >= 6) return 'high';
  if (uniqueNumbers >= 4) return 'medium';
  return 'low';
}

export function riskLabel(level: RiskLevel): string {
  switch (level) {
    case 'protected':
      return 'Protected';
    case 'high':
      return 'High risk';
    case 'medium':
      return 'Medium risk';
    case 'low':
      return 'Low risk';
    default:
      return 'No cards yet';
  }
}

export type BannerTone = 'info' | 'success' | 'action' | 'warning' | 'danger' | 'celebrate';

export interface ActionFeedback {
  headline: string;
  tone: BannerTone;
}

export function feedbackForAction(result: ActionResult, action: TurnActionKey): ActionFeedback {
  if (result.flip_seven) return { headline: 'Flip 7! Seven unique numbers — round bonus banked.', tone: 'celebrate' };
  if (result.bust) return { headline: 'Bust! A duplicate number ended the run.', tone: 'danger' };
  if (result.second_chance_used) return { headline: 'Second Chance saved the run.', tone: 'action' };
  if (result.deferred_action === 'freeze') return { headline: 'Freeze resolved after the Flip Three sequence.', tone: 'action' };
  if (result.deferred_action === 'flip_three') return { headline: 'Nested Flip Three resolved.', tone: 'action' };
  if (result.round_ended || result.outcome?.round_ended) return { headline: 'Round ended.', tone: 'info' };
  switch (action) {
    case 'hit':
      return { headline: 'Card drawn.', tone: 'info' };
    case 'stay':
      return { headline: 'Stayed and banked the round score.', tone: 'success' };
    case 'freeze':
      return { headline: 'Freeze applied to the target.', tone: 'action' };
    case 'flip_three':
      return { headline: 'Flip Three applied to the target.', tone: 'action' };
    default:
      return { headline: 'Action resolved.', tone: 'info' };
  }
}

export function roundSummaryFromResult(result: ActionResult) {
  return result.round_summary || result.outcome?.round_summary || null;
}
