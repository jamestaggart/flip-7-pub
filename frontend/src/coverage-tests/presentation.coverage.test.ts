import { describe, it, expect } from 'vitest';
import {
  cardFamily,
  cardLabel,
  feedbackForAction,
  hasSecondChance,
  riskLabel,
  riskLevel,
  roundSummaryFromResult,
} from '../lib/presentation';

describe('Presentation helper coverage behavior', () => {
  it('maps all card families and labels across action and modifier variants', () => {
    expect(cardFamily({ card_name: '7', value: 7, effect_type: 'number', effect_payload: '' })).toBe('number');
    expect(cardFamily({ card_name: 'Freeze', value: null, effect_type: 'action', effect_payload: 'freeze' })).toBe('freeze');
    expect(cardFamily({ card_name: 'Flip Three', value: null, effect_type: 'action', effect_payload: 'flip_three' })).toBe('flip-three');
    expect(cardFamily({ card_name: 'Second Chance', value: null, effect_type: 'action', effect_payload: 'second_chance' })).toBe('second-chance');
    expect(cardFamily({ card_name: '-2', value: -2, effect_type: 'modifier', effect_payload: '-2' })).toBe('modifier-negative');
    expect(cardFamily({ card_name: 'x2', value: null, effect_type: 'modifier', effect_payload: 'multiplier' })).toBe('multiplier');
    expect(cardFamily({ card_name: '+2', value: null, effect_type: 'modifier', effect_payload: '+2' })).toBe('modifier-positive');

    expect(cardLabel({ card_name: '0', value: 0, effect_type: 'number', effect_payload: '' })).toBe('0');
    expect(cardLabel({ card_name: 'Freeze', value: null, effect_type: 'action', effect_payload: 'freeze' })).toBe('Freeze');
    expect(cardLabel({ card_name: 'Flip Three', value: null, effect_type: 'action', effect_payload: 'flip_three' })).toBe('Flip 3');
    expect(cardLabel({ card_name: 'Second Chance', value: null, effect_type: 'action', effect_payload: 'second_chance' })).toBe('2nd');
  });

  it('detects second chance and computes risk levels and labels across branches', () => {
    expect(hasSecondChance([{ card_name: 'Second Chance', value: null, effect_type: 'action', effect_payload: 'second_chance' }])).toBe(true);
    expect(hasSecondChance([{ card_name: '4', value: 4, effect_type: 'number', effect_payload: '' }])).toBe(false);

    expect(riskLevel(0, 0, false)).toBe('none');
    expect(riskLevel(5, 3, true)).toBe('protected');
    expect(riskLevel(6, 4, false)).toBe('high');
    expect(riskLevel(4, 4, false)).toBe('medium');
    expect(riskLevel(2, 2, false)).toBe('low');

    expect(riskLabel('protected')).toBe('Protected');
    expect(riskLabel('high')).toBe('High risk');
    expect(riskLabel('medium')).toBe('Medium risk');
    expect(riskLabel('low')).toBe('Low risk');
    expect(riskLabel('none')).toBe('No cards yet');
  });

  it('returns action feedback by priority and action fallback', () => {
    expect(feedbackForAction({ flip_seven: true }, 'hit').tone).toBe('celebrate');
    expect(feedbackForAction({ bust: true }, 'hit').tone).toBe('danger');
    expect(feedbackForAction({ second_chance_used: true }, 'hit').headline).toContain('Second Chance');
    expect(feedbackForAction({ deferred_action: 'freeze' }, 'hit').headline).toContain('Freeze resolved');
    expect(feedbackForAction({ deferred_action: 'flip_three' }, 'hit').headline).toContain('Nested Flip Three');
    expect(feedbackForAction({ outcome: { round_ended: true } }, 'hit').headline).toBe('Round ended.');

    expect(feedbackForAction({}, 'hit').headline).toBe('Card drawn.');
    expect(feedbackForAction({}, 'stay').headline).toContain('banked');
    expect(feedbackForAction({}, 'freeze').headline).toContain('Freeze applied');
    expect(feedbackForAction({}, 'flip_three').headline).toContain('Flip Three applied');
  });

  it('builds round summary from direct or nested result payloads', () => {
    const summary = [{ player_id: 1, username: 'alice', score: 7 }];
    expect(roundSummaryFromResult({ round_summary: summary })).toEqual(summary);
    expect(roundSummaryFromResult({ outcome: { round_summary: summary } })).toEqual(summary);
    expect(roundSummaryFromResult({})).toBeNull();
  });
});
