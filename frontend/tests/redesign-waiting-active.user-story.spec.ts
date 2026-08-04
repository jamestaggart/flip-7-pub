import { test, expect } from '@playwright/test';
import {
  advanceTurnsByHitting,
  closeAllGamesViaApi,
  createGame,
  createPendingThreePlayerGameViaApi,
  playerPanel,
  prepareSecondChanceScenarioViaApi,
  startGame,
  uniqueName,
  gotoLobby,
} from './helpers/redesign-helpers';

test('Starting the game shows the redesigned board, deck counter, and player panels', async ({ page }) => {
  const firstPlayer = uniqueName('cedar');
  const secondPlayer = uniqueName('dune');

  await startGame(page, firstPlayer, secondPlayer);

  await expect(page.getByText('Target')).toBeVisible();
  await expect(page.getByText('Deck')).toBeVisible();
  await expect(page.getByText(/^92$/)).toBeVisible();
  await expect(playerPanel(page, firstPlayer)).toContainText('Unique numbers: 1 / 7');
  await expect(playerPanel(page, secondPlayer)).toContainText('Unique numbers: 1 / 7');
  await expect(page.getByLabel('1 cards').first()).toBeVisible();
});

test('Hit advances the turn and updates the active player on the board', async ({ page }) => {
  const firstPlayer = uniqueName('ember');
  const secondPlayer = uniqueName('frost');

  await startGame(page, firstPlayer, secondPlayer);

  await page.getByRole('button', { name: /Hit/ }).click();

  await expect(page.getByRole('heading', { name: new RegExp(`^${secondPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await expect(playerPanel(page, firstPlayer)).toContainText('Waiting');
  await expect(playerPanel(page, secondPlayer)).toContainText('Your turn');
  await expect(playerPanel(page, firstPlayer).getByLabel('2 cards')).toBeVisible();
});

test('Staying for the last two active players opens the round summary and next round flow', async ({ page }) => {
  const firstPlayer = uniqueName('glint');
  const secondPlayer = uniqueName('harbor');

  await startGame(page, firstPlayer, secondPlayer);

  await page.getByRole('button', { name: /Stay/ }).click();
  await expect(page.getByRole('heading', { name: new RegExp(`^${secondPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();

  await page.getByRole('button', { name: /Stay/ }).click();
  await expect(page.getByRole('dialog', { name: 'Round Summary' })).toBeVisible();
  await expect(page.getByText('Banked this round').first()).toBeVisible();

  await page.getByRole('button', { name: 'Next round' }).click();
  await expect(page.getByRole('dialog', { name: 'Round Summary' })).toBeHidden();
  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
});

test('Waiting room opens the rules modal without leaving the game', async ({ page }) => {
  await createGame(page, uniqueName('rulea'), uniqueName('ruleb'));

  await page.getByRole('button', { name: 'How to play' }).click();
  const dialog = page.getByRole('dialog', { name: 'How to Play' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Got it' }).click();

  await expect(page.getByRole('heading', { name: 'Waiting room' })).toBeVisible();
});

test('Waiting room can remove a player before the game starts', async ({ page, request }) => {
  await closeAllGamesViaApi(request);
  const thirdPlayer = uniqueName('extra');
  const game = await createPendingThreePlayerGameViaApi(request, uniqueName('hosta'), uniqueName('hostb'), thirdPlayer);

  await gotoLobby(page);
  await page.getByRole('button', { name: 'Refresh' }).click();
  const gameRow = page.locator('.lobbyRow', { hasText: game.game_code }).first();
  await gameRow.getByRole('button', { name: 'Open' }).click();

  await expect(page.getByRole('heading', { name: 'Waiting room' })).toBeVisible();
  await expect(page.getByText(thirdPlayer)).toBeVisible();
  await page.getByRole('button', { name: `Remove ${thirdPlayer}` }).click();
  await expect(page.getByText(thirdPlayer)).toHaveCount(0);
  await expect(page.getByText(/2 players ready/)).toBeVisible();
});

test('Waiting room close-game flow can be cancelled from the confirmation modal', async ({ page }) => {
  await createGame(page, uniqueName('closea'), uniqueName('closeb'));

  await page.locator('button', { hasText: 'Close game' }).click();
  const dialog = page.getByRole('dialog', { name: 'Close game?' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Keep playing' }).click();

  await expect(page.getByRole('heading', { name: 'Waiting room' })).toBeVisible();
});

test('Waiting room close-game flow returns to the lobby after confirmation', async ({ page }) => {
  await createGame(page, uniqueName('donea'), uniqueName('doneb'));

  await page.locator('button', { hasText: 'Close game' }).click();
  const dialog = page.getByRole('dialog', { name: 'Close game?' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Close game' }).click();

  await expect(page.getByRole('button', { name: 'Create game' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Open games' })).toBeVisible();
});

test('Active board opens the rules modal without losing game context', async ({ page }) => {
  const firstPlayer = uniqueName('boarda');
  const secondPlayer = uniqueName('boardb');
  await startGame(page, firstPlayer, secondPlayer);

  await page.getByRole('button', { name: 'How to play' }).click();
  const dialog = page.getByRole('dialog', { name: 'How to Play' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Got it' }).click();

  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();
});

test('Active board close-game flow can be cancelled from the confirmation modal', async ({ page }) => {
  const firstPlayer = uniqueName('cancela');
  const secondPlayer = uniqueName('cancelb');
  await startGame(page, firstPlayer, secondPlayer);

  await page.getByRole('button', { name: 'Close game' }).click();
  const dialog = page.getByRole('dialog', { name: 'Close game?' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Keep playing' }).click();

  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
});

test('Active board close-game flow returns to the lobby after confirmation', async ({ page }) => {
  await startGame(page, uniqueName('leavea'), uniqueName('leaveb'));

  await page.getByRole('button', { name: 'Close game' }).click();
  const dialog = page.getByRole('dialog', { name: 'Close game?' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Close game' }).click();

  await expect(page.getByRole('button', { name: 'Create game' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Open games' })).toBeVisible();
});

test('Freeze action shows target selection and cancel restores the action panel', async ({ page }) => {
  const firstPlayer = uniqueName('freezea');
  const secondPlayer = uniqueName('freezeb');
  await startGame(page, firstPlayer, secondPlayer);
  await advanceTurnsByHitting(page, 5);

  await expect(page.getByRole('heading', { name: new RegExp(`^${secondPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await page.getByRole('button', { name: /Freeze/ }).click();

  await expect(page.getByRole('heading', { name: 'Choose target for Freeze' })).toBeVisible();
  await expect(page.getByRole('button', { name: firstPlayer })).toBeVisible();
  await expect(page.getByRole('button', { name: `${secondPlayer} (yourself)` })).toBeVisible();

  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByRole('heading', { name: 'Choose target for Freeze' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Freeze/ })).toBeVisible();
});

test('Freeze action can target another active player and resolve cleanly', async ({ page }) => {
  const firstPlayer = uniqueName('frzha');
  const secondPlayer = uniqueName('frzhb');
  await startGame(page, firstPlayer, secondPlayer);
  await advanceTurnsByHitting(page, 5);

  await expect(page.getByRole('heading', { name: new RegExp(`^${secondPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await page.getByRole('button', { name: /Freeze/ }).click();
  await page.getByRole('button', { name: firstPlayer }).click();

  await expect(page.getByRole('status')).toContainText('Freeze applied to the target.');
  await expect(playerPanel(page, firstPlayer)).toContainText('Waiting');
  await expect(playerPanel(page, secondPlayer)).toContainText('Your turn');
  await expect(page.getByRole('button', { name: /Freeze/ })).toHaveCount(0);
});

test('Flip Three action can target another player and resolve the forced draw sequence', async ({ page }) => {
  const firstPlayer = uniqueName('flipa');
  const secondPlayer = uniqueName('flipb');
  await startGame(page, firstPlayer, secondPlayer);
  await advanceTurnsByHitting(page, 10);

  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await page.getByRole('button', { name: /Flip Three/ }).click();
  await expect(page.getByRole('heading', { name: 'Choose target for Flip Three' })).toBeVisible();
  await page.getByRole('button', { name: secondPlayer }).click();

  await expect(page.getByRole('status')).toContainText('Flip 7! Seven unique numbers — round bonus banked.');
  await expect(page.getByRole('dialog', { name: 'Round Summary' })).toBeVisible();
  await expect(page.getByText(secondPlayer).first()).toBeVisible();
});

test('Second Chance visibly saves a duplicate draw without busting the player', async ({ page, request }) => {
  const firstPlayer = uniqueName('scsavea');
  const secondPlayer = uniqueName('scsaveb');
  const game = await prepareSecondChanceScenarioViaApi(request, firstPlayer, secondPlayer);

  await gotoLobby(page);
  await page.getByRole('button', { name: 'Refresh' }).click();
  const gameRow = page.locator('.lobbyRow', { hasText: game.game_code }).first();
  await gameRow.getByRole('button', { name: 'Open' }).click();

  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
  await expect(playerPanel(page, firstPlayer)).toContainText('2nd');
  await page.getByRole('button', { name: /Hit/ }).click();

  await expect(page.getByRole('status')).toContainText('Second Chance saved the run.');
  await expect(playerPanel(page, firstPlayer)).not.toContainText('Bust');
  await expect(playerPanel(page, firstPlayer)).toContainText('5');
  await expect(playerPanel(page, firstPlayer)).not.toContainText('2nd');
});
