import { expect, type APIRequestContext, type Locator, type Page } from '@playwright/test';

const BACKEND_URL = 'http://127.0.0.1:8000';

export function uniqueName(prefix: string) {
  const suffix = `${Date.now()}`.slice(-6);
  const token = Math.floor(Math.random() * 100).toString().padStart(2, '0');
  return `${prefix}-${suffix}${token}`;
}

export function playerPanel(page: Page, name: string): Locator {
  return page.getByRole('region', { name: `${name} panel` });
}

export async function gotoLobby(page: Page) {
  await page.goto('/');
  await expect(page.getByText('Shuffling the deck…')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Create game' })).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('heading', { name: 'Open games' })).toBeVisible();
}

export async function openCreateFlow(page: Page) {
  await page.getByRole('button', { name: 'Create game' }).click();
  await expect(page.getByRole('heading', { name: 'New game' })).toBeVisible();
}

export async function createGame(page: Page, firstPlayer: string, secondPlayer: string) {
  await gotoLobby(page);
  await openCreateFlow(page);
  await page.getByRole('textbox', { name: 'Player 1 name (starts)' }).fill(firstPlayer);
  await page.getByRole('textbox', { name: 'Player 2 name' }).fill(secondPlayer);
  await page.getByRole('button', { name: 'Create & continue' }).click();

  await expect(page.getByRole('heading', { name: 'Waiting room' })).toBeVisible();
  await expect(page.getByText(firstPlayer)).toBeVisible();
  await expect(page.getByText(secondPlayer)).toBeVisible();
  await expect(page.getByText(/Target score 200\./)).toBeVisible();
}

export async function startGame(page: Page, firstPlayer: string, secondPlayer: string) {
  await createGame(page, firstPlayer, secondPlayer);
  await page.getByRole('button', { name: 'Start game' }).click();
  await expect(
    page.getByRole('heading', {
      name: new RegExp(`^${firstPlayer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\'s turn$`),
    }),
  ).toBeVisible();
  await expect(page.getByRole('button', { name: /Hit/ })).toBeVisible();
  await expect(playerPanel(page, firstPlayer)).toContainText('Your turn');
  await expect(playerPanel(page, secondPlayer)).toContainText('Waiting');
}

async function createPlayerViaApi(request: APIRequestContext, name: string) {
  const response = await request.post(`${BACKEND_URL}/api/players/`, {
    data: { username: name, display_name: name },
  });
  expect(response.ok()).toBeTruthy();
  return (await response.json()) as { id: number; username: string; display_name: string };
}

async function listGamesViaApi(request: APIRequestContext) {
  const response = await request.get(`${BACKEND_URL}/api/games/`);
  expect(response.ok()).toBeTruthy();
  return (await response.json()) as Array<{ id: number; game_code: string; status: string }>;
}

export async function closeAllGamesViaApi(request: APIRequestContext) {
  const games = await listGamesViaApi(request);
  for (const game of games) {
    const response = await request.post(`${BACKEND_URL}/api/games/${game.id}/close/`);
    // A game may be closed by another flow between list and close; treat 404 as already closed.
    expect(response.ok() || response.status() === 404).toBeTruthy();
  }
}

export async function createLowTargetGameViaApi(request: APIRequestContext, firstPlayer: string, secondPlayer: string) {
  const first = await createPlayerViaApi(request, firstPlayer);
  const second = await createPlayerViaApi(request, secondPlayer);

  const createResponse = await request.post(`${BACKEND_URL}/api/games/create/`, {
    data: { created_by: first.id, target_score: 1 },
  });
  expect(createResponse.ok()).toBeTruthy();
  const game = (await createResponse.json()) as { id: number; game_code: string };

  const joinResponse = await request.post(`${BACKEND_URL}/api/games/${game.id}/join/`, {
    data: { player_id: second.id, seat_number: 2 },
  });
  expect(joinResponse.ok()).toBeTruthy();

  return game;
}

export async function createPendingGameViaApi(request: APIRequestContext, firstPlayer: string, secondPlayer: string) {
  const first = await createPlayerViaApi(request, firstPlayer);
  const second = await createPlayerViaApi(request, secondPlayer);

  const createResponse = await request.post(`${BACKEND_URL}/api/games/create/`, {
    data: { created_by: first.id, target_score: 200 },
  });
  expect(createResponse.ok()).toBeTruthy();
  const game = (await createResponse.json()) as { id: number; game_code: string };

  const joinResponse = await request.post(`${BACKEND_URL}/api/games/${game.id}/join/`, {
    data: { player_id: second.id, seat_number: 2 },
  });
  expect(joinResponse.ok()).toBeTruthy();

  return game;
}

export async function createPendingThreePlayerGameViaApi(
  request: APIRequestContext,
  firstPlayer: string,
  secondPlayer: string,
  thirdPlayer: string,
) {
  const first = await createPlayerViaApi(request, firstPlayer);
  const second = await createPlayerViaApi(request, secondPlayer);
  const third = await createPlayerViaApi(request, thirdPlayer);

  const createResponse = await request.post(`${BACKEND_URL}/api/games/create/`, {
    data: { created_by: first.id, target_score: 200 },
  });
  expect(createResponse.ok()).toBeTruthy();
  const game = (await createResponse.json()) as { id: number; game_code: string };

  const joinSecondResponse = await request.post(`${BACKEND_URL}/api/games/${game.id}/join/`, {
    data: { player_id: second.id, seat_number: 2 },
  });
  expect(joinSecondResponse.ok()).toBeTruthy();

  const joinThirdResponse = await request.post(`${BACKEND_URL}/api/games/${game.id}/join/`, {
    data: { player_id: third.id, seat_number: 3 },
  });
  expect(joinThirdResponse.ok()).toBeTruthy();

  return game;
}

export async function createStartedGameViaApi(request: APIRequestContext, firstPlayer: string, secondPlayer: string) {
  const game = await createPendingGameViaApi(request, firstPlayer, secondPlayer);
  const startResponse = await request.post(`${BACKEND_URL}/api/games/${game.id}/start_round/`, { data: {} });
  expect(startResponse.ok()).toBeTruthy();
  return game;
}

export async function prepareSecondChanceScenarioViaApi(
  request: APIRequestContext,
  firstPlayer: string,
  secondPlayer: string,
) {
  const game = await createStartedGameViaApi(request, firstPlayer, secondPlayer);

  const [stateResponse, decksResponse, definitionsResponse] = await Promise.all([
    request.get(`${BACKEND_URL}/api/games/${game.id}/state/`),
    request.get(`${BACKEND_URL}/api/decks/`),
    request.get(`${BACKEND_URL}/api/card-definitions/`),
  ]);

  expect(stateResponse.ok()).toBeTruthy();
  expect(decksResponse.ok()).toBeTruthy();
  expect(definitionsResponse.ok()).toBeTruthy();

  const state = (await stateResponse.json()) as { players: Array<{ player_id: number; username: string }> };
  const decks = (await decksResponse.json()) as Array<{ id: number; game: number }>;
  const definitions = (await definitionsResponse.json()) as Array<{ id: number; card_name: string }>;

  const actingPlayer = state.players.find((player) => player.username === firstPlayer);
  expect(actingPlayer).toBeTruthy();

  const deck = decks.find((item) => item.game === game.id);
  expect(deck).toBeTruthy();

  const secondChanceDefinition = definitions.find((item) => item.card_name === 'Second Chance');
  const fiveDefinition = definitions.find((item) => item.card_name === '5');
  expect(secondChanceDefinition).toBeTruthy();
  expect(fiveDefinition).toBeTruthy();

  const secondChanceInstanceResponse = await request.post(`${BACKEND_URL}/api/card-instances/`, {
    data: { card_definition: secondChanceDefinition!.id, game: game.id, deck: deck!.id },
  });
  expect(secondChanceInstanceResponse.ok()).toBeTruthy();
  const secondChanceInstance = (await secondChanceInstanceResponse.json()) as { id: number };

  const secondChanceLocationResponse = await request.post(`${BACKEND_URL}/api/card-locations/`, {
    data: {
      card_instance: secondChanceInstance.id,
      game: game.id,
      zone_type: 'line',
      owner_player: actingPlayer!.player_id,
      position_in_zone: 2,
      is_face_up: true,
    },
  });
  expect(secondChanceLocationResponse.ok()).toBeTruthy();

  const duplicateFiveInstanceResponse = await request.post(`${BACKEND_URL}/api/card-instances/`, {
    data: { card_definition: fiveDefinition!.id, game: game.id, deck: deck!.id },
  });
  expect(duplicateFiveInstanceResponse.ok()).toBeTruthy();
  const duplicateFiveInstance = (await duplicateFiveInstanceResponse.json()) as { id: number };

  const duplicateFiveLocationResponse = await request.post(`${BACKEND_URL}/api/card-locations/`, {
    data: {
      card_instance: duplicateFiveInstance.id,
      game: game.id,
      zone_type: 'deck',
      owner_player: null,
      position_in_zone: 0,
      is_face_up: false,
    },
  });
  expect(duplicateFiveLocationResponse.ok()).toBeTruthy();

  return game;
}

export async function advanceTurnsByHitting(page: Page, count: number) {
  for (let index = 0; index < count; index += 1) {
    const hitButton = page.getByRole('button', { name: /Hit/ });
    await expect(hitButton).toBeVisible();
    await hitButton.click();
  }
}
