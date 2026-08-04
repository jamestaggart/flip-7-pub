import { test, expect } from '@playwright/test';
import {
  closeAllGamesViaApi,
  createGame,
  createPendingGameViaApi,
  gotoLobby,
  openCreateFlow,
  uniqueName,
} from './helpers/redesign-helpers';

test('Lobby and rules modal match the redesigned entry flow', async ({ page }) => {
  await gotoLobby(page);

  await expect(page.getByText('Press-your-luck, pass-and-play.')).toBeVisible();
  await page.getByRole('button', { name: 'How to play' }).click();
  await expect(page.getByRole('dialog', { name: 'How to Play' })).toBeVisible();
  await expect(page.getByText('Draw another card to grow your round score.')).toBeVisible();
  await expect(page.getByText('Automatically cancels the next bust once, then is discarded.')).toBeVisible();
  await page.getByRole('button', { name: 'Got it' }).click();
  await expect(page.getByRole('dialog', { name: 'How to Play' })).toBeHidden();
});

test('Create game flow reaches the waiting room with the configured roster', async ({ page }) => {
  const firstPlayer = uniqueName('alpha');
  const secondPlayer = uniqueName('bravo');

  await createGame(page, firstPlayer, secondPlayer);

  await expect(page.getByText(/^FLIP\d+$/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start game' })).toBeEnabled();
  await expect(page.locator('button', { hasText: 'Close game' })).toBeVisible();
});

test('Create-game shell can return to the lobby', async ({ page }) => {
  await gotoLobby(page);
  await openCreateFlow(page);

  await page.getByRole('button', { name: 'Back to lobby' }).click();

  await expect(page.getByRole('button', { name: 'Create game' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Open games' })).toBeVisible();
});

test('Create-game shell can add and remove a third player row', async ({ page }) => {
  await gotoLobby(page);
  await openCreateFlow(page);

  await page.getByRole('button', { name: '+ Add player' }).click();
  await expect(page.getByRole('textbox', { name: 'Player 3 name' })).toBeVisible();

  await page.getByRole('button', { name: 'Remove player 3' }).click();
  await expect(page.getByRole('textbox', { name: 'Player 3 name' })).toHaveCount(0);
});

test('Create-game shell supports target-score stepper and presets', async ({ page }) => {
  await gotoLobby(page);
  await openCreateFlow(page);

  await expect(page.locator('.stepValue')).toHaveText('200');
  await page.getByRole('button', { name: 'Increase target' }).click();
  await expect(page.locator('.stepValue')).toHaveText('250');
  await page.getByRole('button', { name: 'Decrease target' }).click();
  await expect(page.locator('.stepValue')).toHaveText('200');

  await page.getByRole('button', { name: '500' }).click();
  await expect(page.getByRole('button', { name: '500', pressed: true })).toBeVisible();
  await expect(page.locator('.stepValue')).toHaveText('500');
});

test('Lobby refresh shows a newly created pending game', async ({ page, request }) => {
  await closeAllGamesViaApi(request);
  await gotoLobby(page);
  await expect(page.getByText('No open games yet. Create one to get started.')).toBeVisible();

  const game = await createPendingGameViaApi(request, uniqueName('lobbya'), uniqueName('lobbyb'));
  await page.getByRole('button', { name: 'Refresh' }).click();

  const gameRow = page.locator('.lobbyRow', { hasText: game.game_code }).first();
  await expect(gameRow).toBeVisible();
  await expect(gameRow).toContainText('pending');
});

test('Lobby shows the designed empty state when no games are open', async ({ page, request }) => {
  await closeAllGamesViaApi(request);
  await gotoLobby(page);

  await expect(page.getByText('No open games yet. Create one to get started.')).toBeVisible();
});
