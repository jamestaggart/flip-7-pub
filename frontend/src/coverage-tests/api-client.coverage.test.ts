import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from '../lib/api';

const fetchMock = vi.fn();

describe('API client coverage behavior', () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal('fetch', fetchMock);
  });

  it('throws network_error when fetch rejects', async () => {
    fetchMock.mockRejectedValueOnce(new Error('socket closed'));

    await expect(api.listPlayers()).rejects.toMatchObject({
      message: 'Network request failed. Check your connection and try again.',
      code: 'network_error',
    });
  });

  it('throws invalid_response for successful non-JSON payloads', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      text: async () => '<html>ok</html>',
    });

    await expect(api.listPlayers()).rejects.toMatchObject({
      message: 'The server returned an unexpected response.',
      code: 'invalid_response',
      statusCode: 200,
    });
  });

  it('throws server_error for failing non-JSON payloads', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 503,
      text: async () => '<html>error</html>',
    });

    await expect(api.listPlayers()).rejects.toMatchObject({
      message: 'Server error (503). Please try again.',
      code: 'server_error',
      statusCode: 503,
    });
  });

  it('propagates backend error payload metadata', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 409,
      text: async () =>
        JSON.stringify({
          error: 'Action is not allowed: not the current turn player',
          error_code: 'invalid_turn_actor',
          details: { actor: 2 },
        }),
    });

    await expect(api.takeAction(1, 'hit', 2)).rejects.toMatchObject({
      message: 'Action is not allowed: not the current turn player',
      code: 'invalid_turn_actor',
      statusCode: 409,
      details: { actor: 2 },
    });
  });

  it('returns parsed JSON for successful responses', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      text: async () => JSON.stringify([{ id: 1, username: 'alice' }]),
    });

    await expect(api.listPlayers()).resolves.toEqual([{ id: 1, username: 'alice' }]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('covers all exported api methods on successful responses', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      text: async () => JSON.stringify({ status: 'ok' }),
    });

    await api.listPlayers();
    await api.createPlayer('alice');
    await api.updatePlayer(1, 'Alice');
    await api.listGames();
    await api.createGame(1, 200);
    await api.joinGame(1, 1, 1);
    await api.removePlayer(1, 1);
    await api.startRound(1);
    await api.getState(1);
    await api.closeGame(1);
    await api.getResults(1);
    await api.takeAction(1, 'hit', 1);

    expect(fetchMock).toHaveBeenCalledTimes(12);
  });
});
