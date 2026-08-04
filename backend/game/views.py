from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player, Game, GamePlayer, GameResult, CardDefinition, Deck, CardInstance, CardLocation, Round, Turn, TurnAction
from .serializers import PlayerSerializer, GameSerializer, GamePlayerSerializer, CardDefinitionSerializer, DeckSerializer, CardInstanceSerializer, CardLocationSerializer, RoundSerializer, TurnSerializer, TurnActionSerializer
from .services import (
    apply_round_score,
    build_game_state,
    calculate_round_score_breakdown,
    create_game_code,
    end_round_if_needed,
    finalize_round,
    get_active_players,
    handle_flip_three,
    handle_freeze,
    handle_hit,
    handle_stay,
    start_round,
)


def _error_response(message, code, status_code, details=None):
    return Response(
        {
            'error': message,
            'error_code': code,
            'details': details or {},
        },
        status=status_code,
    )


MIN_PLAYERS = 2
MAX_PLAYERS = 30


def _validate_turn_action(game, player_id, round_obj=None):
    if game.status == 'finished':
        return None, None, _error_response('Game is finished', 'game_finished', status.HTTP_400_BAD_REQUEST)

    if not player_id:
        return None, None, _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

    player = Player.objects.filter(id=player_id).first()
    if not player:
        return None, None, _error_response('Player not found', 'player_not_found', status.HTTP_404_NOT_FOUND)

    membership = GamePlayer.objects.filter(game=game, player=player).first()
    if not membership:
        return None, None, _error_response('Player is not part of this game', 'player_not_in_game', status.HTTP_400_BAD_REQUEST)

    round_obj = round_obj or game.rounds.order_by('-id').first()
    if not round_obj or round_obj.ended_at:
        return None, None, _error_response('No active round', 'no_active_round', status.HTTP_400_BAD_REQUEST)

    if not membership.is_active:
        return None, None, _error_response('Player is not active in this round', 'player_not_active', status.HTTP_400_BAD_REQUEST)

    current_turn = Turn.objects.filter(game=game, round=round_obj).order_by('-id').first()
    if not current_turn:
        return None, None, _error_response('No active turn', 'no_active_turn', status.HTTP_400_BAD_REQUEST)

    if current_turn.acting_player_id != player.id:
        return None, None, _error_response('Action is not allowed: not the current turn player', 'invalid_turn_actor', status.HTTP_409_CONFLICT)

    return player, round_obj, None


def _validate_freeze_target(game, target_player_id):
    if not target_player_id:
        return None, _error_response('target_player_id is required', 'missing_target_player_id', status.HTTP_400_BAD_REQUEST)

    target_player = Player.objects.filter(id=target_player_id).first()
    if not target_player:
        return None, _error_response('Target player not found', 'target_player_not_found', status.HTTP_404_NOT_FOUND)

    target_membership = GamePlayer.objects.filter(game=game, player=target_player).first()
    if not target_membership:
        return None, _error_response('Target player is not part of this game', 'target_not_in_game', status.HTTP_400_BAD_REQUEST)

    if not target_membership.is_active:
        return None, _error_response('Target player is not active in this round', 'target_not_active', status.HTTP_400_BAD_REQUEST)

    return target_player, None


def _get_game_player(game, player_id):
    player = Player.objects.filter(id=player_id).first()
    if not player:
        return None, None, _error_response('Player not found', 'player_not_found', status.HTTP_404_NOT_FOUND)

    membership = GamePlayer.objects.filter(game=game, player=player).first()
    if not membership:
        return None, None, _error_response('Player is not part of this game', 'player_not_in_game', status.HTTP_400_BAD_REQUEST)

    return player, membership, None


def _validate_stay_allowed(game, player):
    has_line_cards = CardLocation.objects.filter(game=game, owner_player=player, zone_type='line').exists()
    if not has_line_cards:
        return _error_response('Player cannot stay without a card in front of them', 'stay_requires_card', status.HTTP_400_BAD_REQUEST)
    return None


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('Invalid game payload', 'validation_error', status.HTTP_400_BAD_REQUEST, serializer.errors)
        game_code = request.data.get('game_code') or create_game_code()
        game = serializer.save(game_code=game_code)

        created_by_id = request.data.get('created_by')
        if created_by_id:
            player = Player.objects.filter(id=created_by_id).first()
            if not player:
                game.delete()
                return _error_response('created_by does not reference a valid player', 'invalid_created_by', status.HTTP_400_BAD_REQUEST)
            GamePlayer.objects.get_or_create(
                game=game,
                player=player,
                defaults={'seat_number': 1},
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        game = self.get_object()
        if game.status == 'finished':
            return _error_response('Cannot join a finished game', 'game_finished', status.HTTP_400_BAD_REQUEST)

        if game.rounds.exists():
            return _error_response('Cannot join a game that has already started', 'game_already_started', status.HTTP_400_BAD_REQUEST)

        player_id = request.data.get('player_id')
        seat_number = request.data.get('seat_number', 1)
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)
        try:
            seat_number = int(seat_number)
        except (TypeError, ValueError):
            return _error_response('seat_number must be an integer greater than 0', 'invalid_seat_number', status.HTTP_400_BAD_REQUEST)

        if seat_number < 1:
            return _error_response('seat_number must be greater than 0', 'invalid_seat_number', status.HTTP_400_BAD_REQUEST)

        player = Player.objects.filter(id=player_id).first()
        if not player:
            return _error_response('Player not found', 'player_not_found', status.HTTP_404_NOT_FOUND)

        existing_membership = GamePlayer.objects.filter(game=game, player=player).first()
        if existing_membership:
            return Response({'status': 'joined', 'game_player_id': existing_membership.id})

        if GamePlayer.objects.filter(game=game).count() >= MAX_PLAYERS:
            return _error_response(f'Game is full (max {MAX_PLAYERS} players)', 'game_full', status.HTTP_400_BAD_REQUEST)

        if GamePlayer.objects.filter(game=game, seat_number=seat_number).exists():
            return _error_response('Seat number is already taken in this game', 'seat_taken', status.HTTP_400_BAD_REQUEST)

        game_player, _ = GamePlayer.objects.get_or_create(game=game, player=player, defaults={'seat_number': seat_number})
        return Response({'status': 'joined', 'game_player_id': game_player.id})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        game = self.get_object()
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def remove_player(self, request, pk=None):
        game = self.get_object()
        if game.rounds.exists():
            return _error_response('Cannot remove players once the game has started', 'game_already_started', status.HTTP_400_BAD_REQUEST)

        player_id = request.data.get('player_id')
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

        membership = GamePlayer.objects.filter(game=game, player_id=player_id).first()
        if not membership:
            return _error_response('Player is not in this game', 'player_not_found', status.HTTP_404_NOT_FOUND)

        if GamePlayer.objects.filter(game=game).count() <= MIN_PLAYERS:
            return _error_response(f'A game needs at least {MIN_PLAYERS} players; close the game instead', 'not_enough_players', status.HTTP_400_BAD_REQUEST)

        membership.delete()
        return Response(build_game_state(game))

    @action(detail=True, methods=['post'])
    def start_round(self, request, pk=None):
        game = self.get_object()
        if game.status == 'finished':
            return _error_response('Cannot start round for a finished game', 'game_finished', status.HTTP_400_BAD_REQUEST)
        if game.game_players.count() < MIN_PLAYERS:
            return _error_response(f'A game needs at least {MIN_PLAYERS} players to start', 'not_enough_players', status.HTTP_400_BAD_REQUEST)
        round_obj, turn = start_round(game)
        return Response({'round_id': round_obj.id, 'turn_id': turn.id, 'state': build_game_state(game)})

    @action(detail=True, methods=['get'])
    def state(self, request, pk=None):
        game = self.get_object()
        return Response(build_game_state(game))

    @action(detail=True, methods=['post'])
    def hit(self, request, pk=None):
        game = self.get_object()
        player_id = request.data.get('player_id')
        player, round_obj, error_response = _validate_turn_action(game, player_id)
        if error_response:
            return error_response
        return Response(handle_hit(round_obj, player))

    @action(detail=True, methods=['post'])
    def stay(self, request, pk=None):
        game = self.get_object()
        player_id = request.data.get('player_id')
        player, round_obj, error_response = _validate_turn_action(game, player_id)
        if error_response:
            return error_response
        stay_error = _validate_stay_allowed(game, player)
        if stay_error:
            return stay_error
        return Response(handle_stay(round_obj, player))

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        game = self.get_object()
        player_id = request.data.get('player_id')
        target_player_id = request.data.get('target_player_id')

        acting_player, round_obj, error_response = _validate_turn_action(game, player_id)
        if error_response:
            return error_response

        target_player, target_error = _validate_freeze_target(game, target_player_id)
        if target_error:
            return target_error

        return Response(handle_freeze(round_obj, acting_player, target_player))

    @action(detail=True, methods=['post'])
    def flip_three(self, request, pk=None):
        game = self.get_object()
        player_id = request.data.get('player_id')
        target_player_id = request.data.get('target_player_id')

        acting_player, round_obj, error_response = _validate_turn_action(game, player_id)
        if error_response:
            return error_response

        target_player, target_error = _validate_freeze_target(game, target_player_id)
        if target_error:
            return target_error

        return Response(handle_flip_three(round_obj, acting_player, target_player))

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        game = self.get_object()
        standings = []

        result_rows = list(GameResult.objects.filter(game=game).select_related('player').order_by('ranking', 'player_id'))
        if result_rows:
            for result in result_rows:
                membership = GamePlayer.objects.filter(game=game, player=result.player).first()
                standings.append({
                    'player_id': result.player_id,
                    'username': result.player.username,
                    'display_name': result.player.display_name or result.player.username,
                    'seat_number': membership.seat_number if membership else None,
                    'total_score': result.score,
                    'is_busted': membership.is_busted if membership else False,
                })
        else:
            for membership in game.game_players.select_related('player').order_by('-final_score', 'seat_number'):
                standings.append({
                    'player_id': membership.player_id,
                    'username': membership.player.username,
                    'display_name': membership.player.display_name or membership.player.username,
                    'seat_number': membership.seat_number,
                    'total_score': membership.final_score or 0,
                    'is_busted': membership.is_busted,
                })

        winner = standings[0] if standings else None
        return Response({
            'game_id': game.id,
            'status': game.status,
            'target_score': game.target_score,
            'winner': winner,
            'standings': standings,
        })

    @action(detail=True, methods=['post'], url_path='rules/validate')
    def rules_validate(self, request, pk=None):
        game = self.get_object()
        action_type = request.data.get('action_type')
        player_id = request.data.get('player_id')
        target_player_id = request.data.get('target_player_id')
        round_obj = game.rounds.order_by('-id').first()

        if action_type not in {'hit', 'stay', 'freeze', 'flip_three'}:
            return Response({'valid': False, 'reason': 'Unsupported action_type'})

        player, validated_round, error_response = _validate_turn_action(game, player_id, round_obj=round_obj)
        if error_response:
            return Response({'valid': False, 'reason': error_response.data.get('error')})

        if action_type in {'freeze', 'flip_three'}:
            _, target_error = _validate_freeze_target(game, target_player_id)
            if target_error:
                return Response({'valid': False, 'reason': target_error.data.get('error')})

        return Response({'valid': True, 'reason': 'Action is valid', 'round_id': validated_round.id, 'player_id': player.id})

    @action(detail=True, methods=['post'], url_path='rules/resolve')
    def rules_resolve(self, request, pk=None):
        game = self.get_object()
        action_type = request.data.get('action_type')
        payload = request.data.get('payload', {})
        player_id = payload.get('player_id')
        target_player_id = payload.get('target_player_id')

        if action_type not in {'hit', 'stay', 'freeze', 'flip_three'}:
            return _error_response('Unsupported action_type', 'unsupported_action_type', status.HTTP_400_BAD_REQUEST)

        acting_player, round_obj, error_response = _validate_turn_action(game, player_id)
        if error_response:
            return error_response

        if action_type == 'hit':
            return Response(handle_hit(round_obj, acting_player))

        if action_type == 'stay':
            return Response(handle_stay(round_obj, acting_player))

        target_player, target_error = _validate_freeze_target(game, target_player_id)
        if target_error:
            return target_error

        if action_type == 'freeze':
            return Response(handle_freeze(round_obj, acting_player, target_player))

        return Response(handle_flip_three(round_obj, acting_player, target_player))


class GamePlayerViewSet(viewsets.ModelViewSet):
    queryset = GamePlayer.objects.all()
    serializer_class = GamePlayerSerializer


class CardDefinitionViewSet(viewsets.ModelViewSet):
    queryset = CardDefinition.objects.all()
    serializer_class = CardDefinitionSerializer


class DeckViewSet(viewsets.ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer


class CardInstanceViewSet(viewsets.ModelViewSet):
    queryset = CardInstance.objects.all()
    serializer_class = CardInstanceSerializer


class CardLocationViewSet(viewsets.ModelViewSet):
    queryset = CardLocation.objects.all()
    serializer_class = CardLocationSerializer


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def _get_round_with_game_check(self, pk, game_pk=None):
        round_obj = self.get_object()
        if game_pk is not None and round_obj.game_id != int(game_pk):
            return None, _error_response('Round does not belong to the specified game', 'round_game_mismatch', status.HTTP_400_BAD_REQUEST)
        return round_obj, None

    @action(detail=True, methods=['post'])
    def hit(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        player, _, error_response = _validate_turn_action(round_obj.game, player_id, round_obj=round_obj)
        if error_response:
            return error_response
        result = handle_hit(round_obj, player)
        return Response(result)

    @action(detail=True, methods=['post'])
    def stay(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        player, _, error_response = _validate_turn_action(round_obj.game, player_id, round_obj=round_obj)
        if error_response:
            return error_response
        stay_error = _validate_stay_allowed(round_obj.game, player)
        if stay_error:
            return stay_error
        result = handle_stay(round_obj, player)
        return Response(result)

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        target_player_id = request.data.get('target_player_id')

        acting_player, _, error_response = _validate_turn_action(round_obj.game, player_id, round_obj=round_obj)
        if error_response:
            return error_response

        target_player, target_error = _validate_freeze_target(round_obj.game, target_player_id)
        if target_error:
            return target_error

        result = handle_freeze(round_obj, acting_player, target_player)
        return Response(result)

    @action(detail=True, methods=['post'])
    def flip_three(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        target_player_id = request.data.get('target_player_id')

        acting_player, _, error_response = _validate_turn_action(round_obj.game, player_id, round_obj=round_obj)
        if error_response:
            return error_response

        target_player, target_error = _validate_freeze_target(round_obj.game, target_player_id)
        if target_error:
            return target_error

        result = handle_flip_three(round_obj, acting_player, target_player)
        return Response(result)

    @action(detail=True, methods=['post'], url_path='score/calculate')
    def score_calculate(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

        player, _, error_response = _get_game_player(round_obj.game, player_id)
        if error_response:
            return error_response

        return Response(calculate_round_score_breakdown(round_obj.game, player, round_obj=round_obj))

    @action(detail=True, methods=['post'], url_path='score/apply')
    def score_apply(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

        player, _, error_response = _get_game_player(round_obj.game, player_id)
        if error_response:
            return error_response

        if round_obj.ended_at:
            breakdown = calculate_round_score_breakdown(round_obj.game, player, round_obj=round_obj)
            membership = GamePlayer.objects.get(game=round_obj.game, player=player)
            return Response({
                'round_id': round_obj.id,
                'player_id': player.id,
                'applied_score': 0,
                'new_total': membership.final_score or 0,
                'already_applied': True,
                'breakdown': breakdown,
            })

        return Response(apply_round_score(round_obj.game, round_obj, player))

    @action(detail=True, methods=['post'], url_path='actions/bust')
    def bust(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

        _, membership, error_response = _get_game_player(round_obj.game, player_id)
        if error_response:
            return error_response

        if membership.is_busted:
            return _error_response('Player is already busted', 'already_busted', status.HTTP_400_BAD_REQUEST)

        membership.is_active = False
        membership.is_busted = True
        membership.save(update_fields=['is_active', 'is_busted'])

        end_result = end_round_if_needed(round_obj)
        return Response({
            'round_id': round_obj.id,
            'player_id': membership.player_id,
            'busted': True,
            'round_status': end_result,
        })

    @action(detail=True, methods=['post'], url_path='actions/flip-seven')
    def flip_seven(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        player_id = request.data.get('player_id')
        if not player_id:
            return _error_response('player_id is required', 'missing_player_id', status.HTTP_400_BAD_REQUEST)

        player, membership, error_response = _get_game_player(round_obj.game, player_id)
        if error_response:
            return error_response

        if not membership.is_active:
            return _error_response('Player is not active in this round', 'player_not_active', status.HTTP_400_BAD_REQUEST)

        score_info = calculate_round_score_breakdown(round_obj.game, player, round_obj=round_obj)
        if score_info['unique_numbers'] < 7:
            return _error_response('Player has not reached 7 unique numbers', 'flip_seven_condition_not_met', status.HTTP_400_BAD_REQUEST)

        round_obj.winner_player = player
        round_obj.save(update_fields=['winner_player'])
        summary = finalize_round(round_obj)
        return Response({
            'round_id': round_obj.id,
            'player_id': player.id,
            'flip_seven': True,
            'round_summary': summary['round_summary'],
        })

    @action(detail=True, methods=['post'], url_path='end-check')
    def end_check(self, request, pk=None, game_pk=None):
        round_obj, mismatch_error = self._get_round_with_game_check(pk, game_pk=game_pk)
        if mismatch_error:
            return mismatch_error
        return Response(end_round_if_needed(round_obj))


class TurnViewSet(viewsets.ModelViewSet):
    queryset = Turn.objects.all()
    serializer_class = TurnSerializer


class TurnActionViewSet(viewsets.ModelViewSet):
    queryset = TurnAction.objects.all()
    serializer_class = TurnActionSerializer
