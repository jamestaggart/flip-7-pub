import { test, expect } from '@playwright/test';
import {
  closeAllGamesViaApi,
  createLowTargetGameViaApi,
  createStartedGameViaApi,
  gotoLobby,
  playerPanel,
  startGame,
  uniqueName,
} from './helpers/redesign-helpers';

test('Reload restores the previously opened game using persisted game id', async ({ page, request }) => {
  await closeAllGamesViaApi(request);
  const firstPlayer = uniqueName('restorea');
  const secondPlayer = uniqueName('restoreb');
  const game = await createStartedGameViaApi(request, firstPlayer, secondPlayer);

  await gotoLobby(page);
  await page.getByRole('button', { name: 'Refresh' }).click();
  const gameRow = page.locator('.lobbyRow', { hasText: game.game_code }).first();
  await gameRow.getByRole('button', { name: 'Open' }).click();

  const firstTurnHeading = page.getByRole('heading', {
    name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`),
  });
  await expect(firstTurnHeading).toBeVisible();
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();

  await page.reload();

  await expect(firstTurnHeading).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();
  await expect(playerPanel(page, firstPlayer)).toContainText('Your turn');
  await expect(playerPanel(page, secondPlayer)).toContainText('Waiting');
});

test('Network failure during an action shows the disconnect modal and reconnect restores play', async ({ page }) => {
  const firstPlayer = uniqueName('neta');
  const secondPlayer = uniqueName('netb');
  await startGame(page, firstPlayer, secondPlayer);

  const hitEndpoint = /http:\/\/localhost:8000\/api\/games\/\d+\/hit\/$/;
  await page.route(hitEndpoint, async (route) => {
    await route.abort('failed');
  });

  await page.getByRole('button', { name: /Hit/ }).click();
  const disconnectDialog = page.getByRole('dialog', { name: 'Connection lost' });
  await expect(disconnectDialog).toBeVisible();
  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();

  await page.unroute(hitEndpoint);
  await disconnectDialog.getByRole('button', { name: 'Reconnect' }).click();
  await expect(disconnectDialog).toBeHidden();
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();
  await expect(page.getByRole('heading', { name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`) })).toBeVisible();
});

test('A failed action shows a dismissible error toast', async ({ page }) => {
  await startGame(page, uniqueName('toasta'), uniqueName('toastb'));

  const hitEndpoint = /http:\/\/localhost:8000\/api\/games\/\d+\/hit\/$/;
  await page.route(hitEndpoint, async (route) => {
    await route.fulfill({
      status: 409,
      contentType: 'application/json',
      body: JSON.stringify({
        error: 'Test conflict while resolving the action.',
        error_code: 'test_conflict',
        details: {},
      }),
    });
  });

  await page.getByRole('button', { name: /Hit/ }).click();
  const alert = page.locator('.errorToast');
  await expect(alert).toBeVisible();
  await expect(alert).toContainText('Test conflict while resolving the action.');
  await alert.getByRole('button', { name: 'Dismiss' }).click();
  await expect(alert).toHaveCount(0);
  await page.unroute(hitEndpoint);
});

test('Pending action lockout prevents duplicate hit submissions', async ({ page }) => {
  await startGame(page, uniqueName('locka'), uniqueName('lockb'));

  const hitEndpoint = /http:\/\/localhost:8000\/api\/games\/\d+\/hit\/$/;
  let hitRequests = 0;
  await page.route(hitEndpoint, async (route) => {
    hitRequests += 1;
    await new Promise((resolve) => setTimeout(resolve, 500));
    await route.continue();
  });

  const hitButton = page.getByRole('button', { name: /Hit/ });
  await hitButton.dblclick();
  await expect(hitButton).toBeDisabled();
  await expect.poll(() => hitRequests, { timeout: 5000 }).toBe(1);
  await expect(hitButton).toBeEnabled({ timeout: 5000 });
  await page.unroute(hitEndpoint);
});

test('A low-target game can be opened from the lobby and finished through the redesigned game-over screen', async ({ page, request }) => {
  const firstPlayer = uniqueName('iris');
  const secondPlayer = uniqueName('yuno');
  const game = await createLowTargetGameViaApi(request, firstPlayer, secondPlayer);

  await gotoLobby(page);
  await page.getByRole('button', { name: 'Refresh' }).click();

  const gameRow = page.locator('.lobbyRow', { hasText: game.game_code }).first();
  await expect(gameRow).toBeVisible();
  await gameRow.getByRole('button', { name: 'Open' }).click();

  await expect(page.getByRole('heading', { name: 'Waiting room' })).toBeVisible();
  await page.getByRole('button', { name: 'Start game' }).click();
  await page.getByRole('button', { name: /Stay/ }).click();
  await page.getByRole('button', { name: /Stay/ }).click();

  await expect(page.getByText('Game over')).toBeVisible();
  await expect(page.getByText(/wins!/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Play again (same settings)' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'New game' })).toBeVisible();
});
