import { describe, expect, it } from 'vitest';
import type { ReactElement, ReactNode } from 'react';
import RootLayout, { metadata } from '../app/layout';

function asElement(node: ReactNode): ReactElement {
  return node as ReactElement;
}

describe('Layout coverage behavior', () => {
  it('exports expected metadata values', () => {
    expect(metadata.title).toBe('Flip 7');
    expect(metadata.description).toBe('A couch co-op turn-based card game');
  });

  it('wraps children with html lang and body', () => {
    const child = <div data-testid="slot">content</div>;
    const tree = RootLayout({ children: child });

    expect(tree.type).toBe('html');
    expect(tree.props.lang).toBe('en');

    const body = asElement(tree.props.children);
    expect(body.type).toBe('body');

    const slottedChild = asElement(body.props.children);
    expect(slottedChild.props['data-testid']).toBe('slot');
  });
});
