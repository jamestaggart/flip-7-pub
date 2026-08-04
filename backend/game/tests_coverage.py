from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch
from rest_framework.test import APIClient, APIRequestFactory

from .models import CardDefinition, CardInstance, Deck, Game, GamePlayer, GameResult, Player, Round, Turn
from .serializers import (
    CardLocationSerializer,
    GamePlayerSerializer,
    PlayerSerializer,
    RoundSerializer,
    TurnSerializer,
)
from .services import (
    _get_shuffle_rng,
    create_game_code,
    end_round_if_needed,
    ensure_game_deck,
    handle_flip_three,
    handle_freeze,
    handle_hit,
)
from .views import (
    GameViewSet,
    RoundViewSet,
    _error_response,
    _get_game_player,
    _validate_freeze_target,
    _validate_stay_allowed,
    _validate_turn_action,
)


class CoverageFocusedTests(TestCase):
    def setUp(self):
        self.player1 = Player.objects.create(username='alice')
        self.player2 = Player.objects.create(username='bob')
        self.player3 = Player.objects.create(username='charlie')
        self.game = Game.objects.create(game_code='FLIP9999', created_by=self.player1)
        GamePlayer.objects.create(game=self.game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=self.game, player=self.player2, seat_number=2)
        self.deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        self.card_definition = CardDefinition.objects.create(card_name='4', value=4, effect_type='number', effect_payload='')
        self.card_instance = CardInstance.objects.create(card_definition=self.card_definition, game=self.game, deck=self.deck)

    def test_player_serializer_trims_username(self):
        serializer = PlayerSerializer(data={'username': '   janedoe   '})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['username'], 'janedoe')

    def test_player_serializer_rejects_short_username(self):
        serializer = PlayerSerializer(data={'username': 'ab'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Username must be at least 3 characters long.', serializer.errors['username'][0])

    def test_game_player_serializer_rejects_invalid_and_duplicate_seats(self):
        serializer = GamePlayerSerializer(data={'game': self.game.id, 'player': self.player3.id, 'seat_number': 0})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Seat number must be greater than 0.', str(serializer.errors))

        serializer = GamePlayerSerializer(data={'game': self.game.id, 'player': self.player3.id, 'seat_number': 1})
        self.assertFalse(serializer.is_valid())
        self.assertIn('must make a unique set', str(serializer.errors))

    def test_game_player_serializer_rejects_duplicate_membership(self):
        serializer = GamePlayerSerializer(data={'game': self.game.id, 'player': self.player1.id, 'seat_number': 3})
        self.assertFalse(serializer.is_valid())
        self.assertIn('must make a unique set', str(serializer.errors))

    def test_card_location_serializer_validates_zone_owner_consistency(self):
        serializer = CardLocationSerializer(data={
            'card_instance': self.card_instance.id,
            'game': self.game.id,
            'zone_type': 'void',
            'owner_player': None,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('zone_type must be one of deck, line, discard.', str(serializer.errors))

        serializer = CardLocationSerializer(data={
            'card_instance': self.card_instance.id,
            'game': self.game.id,
            'zone_type': 'line',
            'owner_player': None,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('owner_player is required for line zone.', str(serializer.errors))

        serializer = CardLocationSerializer(data={
            'card_instance': self.card_instance.id,
            'game': self.game.id,
            'zone_type': 'deck',
            'owner_player': self.player1.id,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('owner_player must be null for deck/discard zones.', str(serializer.errors))

    def test_turn_serializer_rejects_invalid_turn_number_and_non_member_actor(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)

        serializer = TurnSerializer(data={
            'game': self.game.id,
            'round': round_obj.id,
            'turn_number': 0,
            'acting_player': self.player1.id,
            'action_type': 'turn',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('turn_number must be greater than 0.', str(serializer.errors))

        serializer = TurnSerializer(data={
            'game': self.game.id,
            'round': round_obj.id,
            'turn_number': 1,
            'acting_player': self.player3.id,
            'action_type': 'turn',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('acting_player must be a member of this game.', str(serializer.errors))

    def test_validate_turn_action_rejects_finished_game(self):
        self.game.status = 'finished'
        self.game.save(update_fields=['status'])

        _, _, response = _validate_turn_action(self.game, self.player1.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'game_finished')

    def test_validate_turn_action_rejects_missing_player_and_player_not_found(self):
        _, _, response = _validate_turn_action(self.game, None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        _, _, response = _validate_turn_action(self.game, 99999)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

    def test_validate_turn_action_rejects_non_member_no_active_round_not_active_no_turn_not_actor(self):
        _, _, response = _validate_turn_action(self.game, self.player3.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'player_not_in_game')

        _, _, response = _validate_turn_action(self.game, self.player1.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_round')

        round_obj = Round.objects.create(game=self.game, round_number=1)
        membership = GamePlayer.objects.get(game=self.game, player=self.player1)
        membership.is_active = False
        membership.save(update_fields=['is_active'])

        _, _, response = _validate_turn_action(self.game, self.player1.id, round_obj=round_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'player_not_active')

        membership.is_active = True
        membership.save(update_fields=['is_active'])

        _, _, response = _validate_turn_action(self.game, self.player1.id, round_obj=round_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player2, action_type='turn')
        _, _, response = _validate_turn_action(self.game, self.player1.id, round_obj=round_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['error_code'], 'invalid_turn_actor')

    def test_validate_freeze_target_and_stay_allowed_errors(self):
        target, response = _validate_freeze_target(self.game, None)
        self.assertIsNone(target)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_target_player_id')

        target, response = _validate_freeze_target(self.game, 99999)
        self.assertIsNone(target)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'target_player_not_found')

        target, response = _validate_freeze_target(self.game, self.player3.id)
        self.assertIsNone(target)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'target_not_in_game')

        membership = GamePlayer.objects.get(game=self.game, player=self.player2)
        membership.is_active = False
        membership.save(update_fields=['is_active'])
        target, response = _validate_freeze_target(self.game, self.player2.id)
        self.assertIsNone(target)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'target_not_active')

        stay_response = _validate_stay_allowed(self.game, self.player1)
        self.assertEqual(stay_response.status_code, 400)
        self.assertEqual(stay_response.data['error_code'], 'stay_requires_card')

    def test_error_response_payload_shape(self):
        response = _error_response('Example error', 'example_code', 422, {'field': 'value'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data['error'], 'Example error')
        self.assertEqual(response.data['error_code'], 'example_code')
        self.assertEqual(response.data['details']['field'], 'value')

    def test_create_game_code_uses_six_digit_fallback_after_many_collisions(self):
        Game.objects.create(game_code='FLIP1111', created_by=self.player1)

        with patch('game.services.random.randint', side_effect=[1111] * 50 + [654321]):
            self.assertEqual(create_game_code(), 'FLIP654321')

    def test_get_shuffle_rng_seeded_path_is_deterministic(self):
        with patch.dict('os.environ', {'FLIP7_TEST_SEED': 'seed-a'}, clear=False):
            rng1 = _get_shuffle_rng()
            rng2 = _get_shuffle_rng()

        self.assertEqual(rng1.randint(1, 1000000), rng2.randint(1, 1000000))

    def test_handle_hit_returns_deck_empty_message_when_no_cards_are_drawable(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')

        ensure_game_deck(self.game)
        for location in self.game.card_locations.filter(zone_type='deck'):
            location.zone_type = 'line'
            location.owner_player = self.player1
            location.save(update_fields=['zone_type', 'owner_player'])

        result = handle_hit(round_obj, self.player1)
        self.assertFalse(result['bust'])
        self.assertEqual(result['message'], 'Deck is empty')

    def test_handle_flip_three_depth_limit_guard_returns_message(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        result = handle_flip_three(round_obj, self.player1, self.player2, depth=4)

        self.assertFalse(result['round_ended'])
        self.assertEqual(result['message'], 'Flip Three depth limit reached')

    def test_handle_freeze_with_only_actor_remaining_has_no_next_turn(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)

        result = handle_freeze(round_obj, self.player1, self.player2)

        self.assertFalse(result['round_ended'])
        self.assertIsNone(result['next_turn_player_id'])
        target_membership = GamePlayer.objects.get(game=self.game, player=self.player2)
        self.assertFalse(target_membership.is_active)

    def test_end_round_if_needed_short_circuits_when_round_already_ended(self):
        round_obj = Round.objects.create(game=self.game, round_number=1, ended_at=timezone.now())

        result = end_round_if_needed(round_obj)

        self.assertTrue(result['round_ended'])
        self.assertEqual(result['round_summary'], [])

    def test_handle_flip_three_processes_deferred_nested_flip_three_action(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        nested_definition = CardDefinition.objects.create(
            card_name='Flip Three',
            value=None,
            effect_type='action',
            effect_payload='flip_three',
            is_special=True,
        )
        nested_card = CardInstance.objects.create(card_definition=nested_definition, game=self.game, deck=self.deck)

        with patch('game.services.draw_card_for_player', side_effect=[nested_card, None, None]):
            result = handle_flip_three(round_obj, self.player1, self.player2)

        self.assertFalse(result['round_ended'])
        self.assertEqual(result.get('deferred_action'), 'flip_three')
        self.assertGreaterEqual(len(result.get('drawn_cards', [])), 1)


class ViewAndSerializerCoverageEdgeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.player1 = Player.objects.create(username='viewalice')
        self.player2 = Player.objects.create(username='viewbob')
        self.player3 = Player.objects.create(username='viewcharlie')

        self.join_game = Game.objects.create(game_code='JOIN1001', created_by=self.player1)
        self.join_membership1 = GamePlayer.objects.create(game=self.join_game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=self.join_game, player=self.player2, seat_number=2)

        self.action_game = Game.objects.create(game_code='ACT1001', created_by=self.player1, status='active')
        self.action_membership1 = GamePlayer.objects.create(game=self.action_game, player=self.player1, seat_number=1)
        self.action_membership2 = GamePlayer.objects.create(game=self.action_game, player=self.player2, seat_number=2)
        self.round_obj = Round.objects.create(game=self.action_game, round_number=1)
        Turn.objects.create(
            game=self.action_game,
            round=self.round_obj,
            turn_number=1,
            acting_player=self.player1,
            action_type='turn',
        )

        self.deck = Deck.objects.create(game=self.join_game, deck_name='Coverage Deck', deck_type='main')
        self.card_definition = CardDefinition.objects.create(card_name='7', value=7, effect_type='number', effect_payload='')
        self.card_instance = CardInstance.objects.create(card_definition=self.card_definition, game=self.join_game, deck=self.deck)

    def test_serializer_success_paths_cover_validate_returns(self):
        serializer = GamePlayerSerializer(data={'game': self.join_game.id, 'player': self.player3.id, 'seat_number': 3})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer = GamePlayerSerializer(
            instance=self.join_membership1,
            data={'game': self.join_game.id, 'player': self.player1.id, 'seat_number': 1},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        location_serializer = CardLocationSerializer(
            data={
                'card_instance': self.card_instance.id,
                'game': self.join_game.id,
                'zone_type': 'line',
                'owner_player': self.player1.id,
            }
        )
        self.assertTrue(location_serializer.is_valid(), location_serializer.errors)

        round_serializer = RoundSerializer(data={'game': self.join_game.id, 'round_number': 1})
        self.assertTrue(round_serializer.is_valid(), round_serializer.errors)

        invalid_round = RoundSerializer(data={'game': self.join_game.id, 'round_number': 0})
        self.assertFalse(invalid_round.is_valid())

        turn_serializer = TurnSerializer(
            data={
                'game': self.action_game.id,
                'round': self.round_obj.id,
                'turn_number': 2,
                'acting_player': self.player1.id,
                'action_type': 'turn',
            }
        )
        self.assertTrue(turn_serializer.is_valid(), turn_serializer.errors)

    def test_game_player_serializer_raises_custom_duplicate_errors_and_allows_missing_game_player_attrs(self):
        serializer = GamePlayerSerializer()

        with self.assertRaises(Exception) as seat_error:
            serializer.validate({'game': self.join_game, 'player': self.player3, 'seat_number': 1})
        self.assertIn('Seat number is already taken in this game.', str(seat_error.exception))

        with self.assertRaises(Exception) as player_error:
            serializer.validate({'game': self.join_game, 'player': self.player1, 'seat_number': 3})
        self.assertIn('Player is already part of this game.', str(player_error.exception))

        validated = serializer.validate({'seat_number': 4})
        self.assertEqual(validated['seat_number'], 4)

    def test_get_game_player_returns_expected_errors_and_success(self):
        _, _, response = _get_game_player(self.join_game, 999999)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

        outsider = Player.objects.create(username='viewoutsider')
        _, _, response = _get_game_player(self.join_game, outsider.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'player_not_in_game')

        player, membership, response = _get_game_player(self.join_game, self.player1.id)
        self.assertIsNone(response)
        self.assertEqual(player.id, self.player1.id)
        self.assertEqual(membership.id, self.join_membership1.id)

    def test_join_endpoint_handles_missing_invalid_and_not_found_player_inputs(self):
        response = self.client.post(f'/api/games/{self.join_game.id}/join/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        response = self.client.post(
            f'/api/games/{self.join_game.id}/join/',
            {'player_id': self.player3.id, 'seat_number': 'abc'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'invalid_seat_number')

        response = self.client.post(
            f'/api/games/{self.join_game.id}/join/',
            {'player_id': self.player3.id, 'seat_number': 0},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'invalid_seat_number')

        response = self.client.post(
            f'/api/games/{self.join_game.id}/join/',
            {'player_id': 999999, 'seat_number': 3},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

    def test_join_endpoint_returns_existing_membership_when_player_already_joined(self):
        response = self.client.post(
            f'/api/games/{self.join_game.id}/join/',
            {'player_id': self.player1.id, 'seat_number': 1},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'joined')
        self.assertEqual(response.data['game_player_id'], self.join_membership1.id)

    def test_game_create_succeeds_without_created_by_and_generates_code(self):
        response = self.client.post('/api/games/create/', {'target_score': 250}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(str(response.data['game_code']).startswith('FLIP'))

    def test_remove_player_requires_player_id(self):
        response = self.client.post(f'/api/games/{self.join_game.id}/remove_player/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

    def test_state_endpoint_returns_current_game_state_payload(self):
        response = self.client.get(f'/api/games/{self.join_game.id}/state/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['game_id'], self.join_game.id)

    def test_results_endpoint_uses_persisted_game_results_rows(self):
        GameResult.objects.create(game=self.join_game, player=self.player1, score=42, ranking=1, is_winner=True)

        response = self.client.get(f'/api/games/{self.join_game.id}/results/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['standings'][0]['player_id'], self.player1.id)
        self.assertEqual(response.data['standings'][0]['total_score'], 42)

    def test_rules_validate_reports_target_validation_errors_for_targeted_actions(self):
        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target',
            return_value=(None, _error_response('Target player not found', 'target_player_not_found', 404)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/validate/',
                {'action_type': 'freeze', 'player_id': self.player1.id, 'target_player_id': 999999},
                format='json',
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['reason'], 'Target player not found')

    def test_rules_validate_returns_true_for_valid_freeze_target(self):
        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(self.player2, None)
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/validate/',
                {'action_type': 'freeze', 'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['round_id'], self.round_obj.id)

    def test_rules_validate_returns_false_for_unsupported_and_turn_validation_errors(self):
        response = self.client.post(
            f'/api/games/{self.action_game.id}/rules/validate/',
            {'action_type': 'skip', 'player_id': self.player1.id},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['reason'], 'Unsupported action_type')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/validate/',
                {'action_type': 'hit', 'player_id': self.player1.id},
                format='json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['reason'], 'No active turn')

    def test_rules_resolve_handles_unsupported_and_validation_error_branches(self):
        response = self.client.post(
            f'/api/games/{self.action_game.id}/rules/resolve/',
            {'action_type': 'skip', 'payload': {'player_id': self.player1.id}},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'unsupported_action_type')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/resolve/',
                {'action_type': 'hit', 'payload': {'player_id': self.player1.id}},
                format='json',
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

    def test_rules_resolve_returns_target_validation_error_for_targeted_actions(self):
        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target',
            return_value=(None, _error_response('Target player not found', 'target_player_not_found', 404)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/resolve/',
                {'action_type': 'freeze', 'payload': {'player_id': self.player1.id, 'target_player_id': 999999}},
                format='json',
            )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'target_player_not_found')

    def test_game_create_returns_invalid_created_by_after_save_cleanup_branch(self):
        fake_game = MagicMock()
        fake_serializer = MagicMock()
        fake_serializer.is_valid.return_value = True
        fake_serializer.save.return_value = fake_game

        request = self.factory.post('/api/games/create/', {'created_by': 999999}, format='json')
        view = GameViewSet.as_view({'post': 'create'})

        with patch.object(GameViewSet, 'get_serializer', return_value=fake_serializer), patch(
            'game.views.Player.objects.filter'
        ) as player_filter:
            player_filter.return_value.first.return_value = None
            response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'invalid_created_by')
        fake_game.delete.assert_called_once()

    def test_game_flip_three_returns_turn_and_target_validation_errors(self):
        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/flip_three/',
                {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target',
            return_value=(None, _error_response('Target player not found', 'target_player_not_found', 404)),
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/flip_three/',
                {'player_id': self.player1.id, 'target_player_id': 999999},
                format='json',
            )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'target_player_not_found')

    def test_round_viewset_actions_cover_mismatch_and_validation_error_return_paths(self):
        hit_view = RoundViewSet.as_view({'post': 'hit'})
        stay_view = RoundViewSet.as_view({'post': 'stay'})
        freeze_view = RoundViewSet.as_view({'post': 'freeze'})
        flip_three_view = RoundViewSet.as_view({'post': 'flip_three'})

        request = self.factory.post('/api/rounds/x/hit/', {'player_id': self.player1.id}, format='json')
        response = hit_view(request, pk=self.round_obj.id, game_pk=self.join_game.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            request = self.factory.post('/api/rounds/x/hit/', {'player_id': self.player1.id}, format='json')
            response = hit_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        request = self.factory.post('/api/rounds/x/stay/', {'player_id': self.player1.id}, format='json')
        response = stay_view(request, pk=self.round_obj.id, game_pk=self.join_game.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            request = self.factory.post('/api/rounds/x/stay/', {'player_id': self.player1.id}, format='json')
            response = stay_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        request = self.factory.post(
            '/api/rounds/x/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = freeze_view(request, pk=self.round_obj.id, game_pk=self.join_game.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            request = self.factory.post(
                '/api/rounds/x/freeze/',
                {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )
            response = freeze_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(self.player2, None)
        ), patch('game.views.handle_freeze', return_value={'result': 'freeze'}):
            request = self.factory.post(
                '/api/rounds/x/freeze/',
                {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )
            response = freeze_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], 'freeze')

        request = self.factory.post(
            '/api/rounds/x/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = flip_three_view(request, pk=self.round_obj.id, game_pk=self.join_game.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        with patch(
            'game.views._validate_turn_action',
            return_value=(None, None, _error_response('No active turn', 'no_active_turn', 400)),
        ):
            request = self.factory.post(
                '/api/rounds/x/flip_three/',
                {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )
            response = flip_three_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'no_active_turn')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target',
            return_value=(None, _error_response('Target player not found', 'target_player_not_found', 404)),
        ):
            request = self.factory.post(
                '/api/rounds/x/flip_three/',
                {'player_id': self.player1.id, 'target_player_id': 999999},
                format='json',
            )
            response = flip_three_view(request, pk=self.round_obj.id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'target_player_not_found')

    def test_rules_resolve_routes_to_stay_freeze_and_flip_three_handlers(self):
        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views.handle_stay', return_value={'action': 'stay'}
        ):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/resolve/',
                {'action_type': 'stay', 'payload': {'player_id': self.player1.id}},
                format='json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['action'], 'stay')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(self.player2, None)
        ), patch('game.views.handle_freeze', return_value={'action': 'freeze'}):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/resolve/',
                {
                    'action_type': 'freeze',
                    'payload': {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                },
                format='json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['action'], 'freeze')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(self.player2, None)
        ), patch('game.views.handle_flip_three', return_value={'action': 'flip_three'}):
            response = self.client.post(
                f'/api/games/{self.action_game.id}/rules/resolve/',
                {
                    'action_type': 'flip_three',
                    'payload': {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                },
                format='json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['action'], 'flip_three')

    def test_round_action_endpoints_cover_hit_stay_freeze_and_flip_three_paths(self):
        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views.handle_hit', return_value={'result': 'hit'}
        ):
            response = self.client.post(f'/api/rounds/{self.round_obj.id}/hit/', {'player_id': self.player1.id}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], 'hit')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_stay_allowed', return_value=None
        ), patch('game.views.handle_stay', return_value={'result': 'stay'}):
            response = self.client.post(f'/api/rounds/{self.round_obj.id}/stay/', {'player_id': self.player1.id}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], 'stay')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_stay_allowed',
            return_value=_error_response('Player cannot stay without a card in front of them', 'stay_requires_card', 400),
        ):
            response = self.client.post(f'/api/rounds/{self.round_obj.id}/stay/', {'player_id': self.player1.id}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'stay_requires_card')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(None, _error_response('Target player not found', 'target_player_not_found', 404))
        ):
            response = self.client.post(
                f'/api/rounds/{self.round_obj.id}/freeze/',
                {'player_id': self.player1.id, 'target_player_id': 999999},
                format='json',
            )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'target_player_not_found')

        with patch('game.views._validate_turn_action', return_value=(self.player1, self.round_obj, None)), patch(
            'game.views._validate_freeze_target', return_value=(self.player2, None)
        ), patch('game.views.handle_flip_three', return_value={'result': 'flip_three'}):
            response = self.client.post(
                f'/api/rounds/{self.round_obj.id}/flip_three/',
                {'player_id': self.player1.id, 'target_player_id': self.player2.id},
                format='json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], 'flip_three')

    def test_round_nested_endpoints_cover_mismatch_and_missing_player_paths(self):
        response = self.client.post(
            f'/api/games/{self.join_game.id}/rounds/{self.round_obj.id}/score/calculate/',
            {'player_id': self.player1.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        response = self.client.post(f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/score/calculate/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        response = self.client.post(
            f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/score/calculate/',
            {'player_id': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

        response = self.client.post(f'/api/games/{self.join_game.id}/rounds/{self.round_obj.id}/score/apply/', {'player_id': self.player1.id}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        response = self.client.post(f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/score/apply/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        response = self.client.post(
            f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/score/apply/',
            {'player_id': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

    def test_round_bust_and_flip_seven_endpoints_cover_guard_branches(self):
        response = self.client.post(
            f'/api/games/{self.join_game.id}/rounds/{self.round_obj.id}/actions/bust/',
            {'player_id': self.player1.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        response = self.client.post(f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/actions/bust/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        response = self.client.post(
            f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/actions/bust/',
            {'player_id': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

        response = self.client.post(
            f'/api/games/{self.join_game.id}/rounds/{self.round_obj.id}/actions/flip-seven/',
            {'player_id': self.player1.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')

        response = self.client.post(f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/actions/flip-seven/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'missing_player_id')

        response = self.client.post(
            f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/actions/flip-seven/',
            {'player_id': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error_code'], 'player_not_found')

        self.action_membership1.is_active = False
        self.action_membership1.save(update_fields=['is_active'])
        response = self.client.post(
            f'/api/games/{self.action_game.id}/rounds/{self.round_obj.id}/actions/flip-seven/',
            {'player_id': self.player1.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'player_not_active')

    def test_end_check_returns_round_game_mismatch_for_wrong_game_scope(self):
        response = self.client.post(f'/api/games/{self.join_game.id}/rounds/{self.round_obj.id}/end-check/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_code'], 'round_game_mismatch')
