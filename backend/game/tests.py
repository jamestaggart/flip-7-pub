from django.test import TestCase
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APIRequestFactory
from unittest.mock import patch
from .models import Player, Game, GamePlayer, GameResult, Round, Turn, Deck, CardDefinition, CardInstance, CardLocation
from .services import DECK_COMPOSITION, start_round, handle_hit, handle_stay, handle_freeze, handle_flip_three, finalize_round, draw_card_for_player
from .services import calculate_round_score, calculate_round_score_breakdown, resolve_second_chance_draw
from .views import GameViewSet, RoundViewSet, PlayerViewSet


class Flip7GameServiceTests(TestCase):
    def setUp(self):
        self.player1 = Player.objects.create(username='alice')
        self.player2 = Player.objects.create(username='bob')
        self.game = Game.objects.create(game_code='FLIP1234', created_by=self.player1)
        GamePlayer.objects.create(game=self.game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=self.game, player=self.player2, seat_number=2)

    def test_start_round_creates_round_and_turn(self):
        round_obj, turn = start_round(self.game)
        self.assertEqual(round_obj.round_number, 1)
        self.assertEqual(turn.acting_player, self.player1)

    def test_start_round_uses_expected_deck_composition_size(self):
        start_round(self.game)
        self.assertEqual(sum(DECK_COMPOSITION.values()), 94)
        self.assertEqual(CardInstance.objects.filter(game=self.game).count(), 94)

    # FR-05 / US-R04 and FR-06 / US-R05 traceability.
    def test_hit_and_stay_flow(self):
        round_obj, turn = start_round(self.game)
        result = handle_hit(round_obj, self.player1)
        self.assertIn('bust', result)
        self.assertIn('flip_seven', result)
        result = handle_stay(round_obj, self.player2)
        self.assertIn('round_ended', result)

    def test_fr05_us_r04_hit_adds_one_card_and_advances_turn(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        existing = CardDefinition.objects.create(card_name='3', value=3, effect_type='number', effect_payload='')
        draw = CardDefinition.objects.create(card_name='8', value=8, effect_type='number', effect_payload='')
        existing_instance = CardInstance.objects.create(card_definition=existing, game=self.game, deck=deck)
        draw_instance = CardInstance.objects.create(card_definition=draw, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_instance, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=1)
        CardLocation.objects.create(card_instance=draw_instance, game=self.game, zone_type='deck', position_in_zone=1)

        before_count = CardLocation.objects.filter(game=self.game, zone_type='line', owner_player=self.player1).count()
        result = handle_hit(round_obj, self.player1)
        after_count = CardLocation.objects.filter(game=self.game, zone_type='line', owner_player=self.player1).count()

        self.assertFalse(result['bust'])
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(result['next_turn_player_id'], self.player2.id)

    def test_fr06_us_r05_stay_banks_score_and_deactivates_player(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        seven = CardDefinition.objects.create(card_name='7', value=7, effect_type='number', effect_payload='')
        plus_two = CardDefinition.objects.create(card_name='+2', value=None, effect_type='modifier', effect_payload='+2')
        seven_instance = CardInstance.objects.create(card_definition=seven, game=self.game, deck=deck)
        plus_two_instance = CardInstance.objects.create(card_definition=plus_two, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=seven_instance, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=1)
        CardLocation.objects.create(card_instance=plus_two_instance, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=2)

        expected_score, _ = calculate_round_score(self.game, self.player1)
        result = handle_stay(round_obj, self.player1)
        membership = GamePlayer.objects.get(game=self.game, player=self.player1)

        self.assertFalse(membership.is_active)
        self.assertEqual(result['next_turn_player_id'], self.player2.id)
        self.assertFalse(result['round_ended'])
        self.assertEqual(calculate_round_score(self.game, self.player1)[0], expected_score)

    def test_create_game_assigns_generated_code(self):
        factory = APIRequestFactory()
        view = GameViewSet.as_view({'post': 'create'})
        request = factory.post('/api/games/', {'created_by': self.player1.id})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        game = Game.objects.get(id=response.data['id'])
        self.assertTrue(game.game_code.startswith('FLIP'))

    def test_create_game_auto_adds_creator_as_player(self):
        factory = APIRequestFactory()
        view = GameViewSet.as_view({'post': 'create'})
        request = factory.post('/api/games/', {'created_by': self.player1.id})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        game = Game.objects.get(id=response.data['id'])
        self.assertTrue(game.game_players.filter(player=self.player1).exists())

    def test_create_game_retries_when_generated_code_collides(self):
        Game.objects.create(game_code='FLIP4321', created_by=self.player1)
        factory = APIRequestFactory()
        view = GameViewSet.as_view({'post': 'create'})
        with patch('game.services.random.randint', side_effect=[4321, 4321, 5678]):
            request = factory.post('/api/games/', {'created_by': self.player1.id})
            response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.get(id=response.data['id']).game_code, 'FLIP5678')

    def test_get_game_returns_metadata_and_status(self):
        view = GameViewSet.as_view({'get': 'retrieve'})
        request = APIRequestFactory().get(f'/api/games/{self.game.id}/')
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.game.id)
        self.assertEqual(response.data['game_code'], 'FLIP1234')
        self.assertEqual(response.data['status'], 'pending')

    def test_get_missing_game_returns_404(self):
        view = GameViewSet.as_view({'get': 'retrieve'})
        request = APIRequestFactory().get('/api/games/99999/')
        response = view(request, pk=99999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_game_hit_and_stay_actions_require_player_id(self):
        game = Game.objects.create(game_code='FLIP9999', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post('/api/games/1/hit/', {})
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # FR-07 / US-R04 traceability.
    def test_hit_rejects_non_current_turn_player(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/hit/',
            {'player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('not the current turn player', response.data['error'])

    # FR-07 / US-R04 traceability.
    def test_stay_rejects_non_current_turn_player(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'stay'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/stay/',
            {'player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('not the current turn player', response.data['error'])

    # FR-07 / US-R04 traceability.
    def test_hit_rejects_inactive_player(self):
        start_round(self.game)
        game_player = GamePlayer.objects.get(game=self.game, player=self.player1)
        game_player.is_active = False
        game_player.save()

        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/hit/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not active', response.data['error'])

    # FR-07 / US-R04 traceability.
    def test_stay_rejects_inactive_player(self):
        start_round(self.game)
        game_player = GamePlayer.objects.get(game=self.game, player=self.player1)
        game_player.is_active = False
        game_player.save()

        view = GameViewSet.as_view({'post': 'stay'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/stay/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not active', response.data['error'])

    def test_stay_rejects_player_with_no_cards_in_line(self):
        round_obj, _ = start_round(self.game)
        CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line').delete()

        view = GameViewSet.as_view({'post': 'stay'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/stay/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'stay_requires_card')
        self.assertFalse(round_obj.ended_at)

    def test_join_game_adds_player_membership_successfully(self):
        newcomer = Player.objects.create(username='charlie')
        view = GameViewSet.as_view({'post': 'join'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/join/',
            {'player_id': newcomer.id, 'seat_number': 3},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'joined')
        self.assertTrue(GamePlayer.objects.filter(game=self.game, player=newcomer, seat_number=3).exists())

    # FR-30 / US-R28 traceability.
    def test_start_round_endpoint_increments_round_number_and_sets_starting_player(self):
        view = GameViewSet.as_view({'post': 'start_round'})

        request_one = APIRequestFactory().post(f'/api/games/{self.game.id}/start_round/', {}, format='json')
        response_one = view(request_one, pk=self.game.id)
        self.assertEqual(response_one.status_code, status.HTTP_200_OK)

        round_one = Round.objects.get(id=response_one.data['round_id'])
        first_turn = Turn.objects.get(id=response_one.data['turn_id'])
        self.assertEqual(round_one.round_number, 1)
        self.assertEqual(first_turn.acting_player_id, self.player1.id)

        request_two = APIRequestFactory().post(f'/api/games/{self.game.id}/start_round/', {}, format='json')
        response_two = view(request_two, pk=self.game.id)
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)

        round_two = Round.objects.get(id=response_two.data['round_id'])
        self.assertEqual(round_two.round_number, 2)

    def test_freeze_deactivates_target_player(self):
        start_round(self.game)

        view = GameViewSet.as_view({'post': 'freeze'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['target_player_id'], self.player2.id)
        self.assertFalse(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

    def test_freeze_rejects_inactive_target_player(self):
        start_round(self.game)

        target_membership = GamePlayer.objects.get(game=self.game, player=self.player2)
        target_membership.is_active = False
        target_membership.save()

        view = GameViewSet.as_view({'post': 'freeze'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Target player is not active', response.data['error'])

    def test_freeze_rejects_when_actor_is_not_current_turn_player(self):
        start_round(self.game)

        view = GameViewSet.as_view({'post': 'freeze'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player2.id, 'target_player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('not the current turn player', response.data['error'])

    # FR-17 / US-R15 traceability.
    def test_hit_uses_second_chance_and_prevents_bust(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        second_chance = CardDefinition.objects.create(card_name='Second Chance', value=None, effect_type='action', effect_payload='second_chance')

        existing_number = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_number, game=self.game, zone_type='line', owner_player=self.player1)

        existing_second_chance = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_second_chance, game=self.game, zone_type='line', owner_player=self.player1)

        duplicate_draw = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate_draw, game=self.game, zone_type='deck')

        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/hit/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['bust'])
        self.assertTrue(response.data['second_chance_used'])
        self.assertEqual(
            CardLocation.objects.filter(card_instance=existing_second_chance).order_by('-id').first().zone_type,
            'discard',
        )
        self.assertEqual(
            CardLocation.objects.filter(card_instance=duplicate_draw).order_by('-id').first().zone_type,
            'discard',
        )

    # FR-23 / US-R21 traceability.
    def test_flip_three_draws_up_to_three_cards_for_target(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in [1, 2, 3]:
            definition = CardDefinition.objects.create(card_name=str(value), value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='deck')

        view = GameViewSet.as_view({'post': 'flip_three'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['drawn_cards']), 3)
        self.assertFalse(response.data['bust'])
        self.assertEqual(CardLocation.objects.filter(game=self.game, owner_player=self.player2, zone_type='line').count(), 3)

    # FR-18 / US-R16 traceability.
    def test_flip_three_passes_extra_second_chance_to_active_player(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        second_chance = CardDefinition.objects.create(card_name='Second Chance', value=None, effect_type='action', effect_payload='second_chance')

        existing_second_chance = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_second_chance, game=self.game, zone_type='line', owner_player=self.player2)

        drawn_second_chance = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=drawn_second_chance, game=self.game, zone_type='deck')

        view = GameViewSet.as_view({'post': 'flip_three'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            CardLocation.objects.filter(card_instance=drawn_second_chance).order_by('-id').first().owner_player_id,
            self.player1.id,
        )

    # FR-08 / US-R06 and FR-24 / US-R22 traceability.
    def test_flip_three_stops_early_when_target_busts(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        existing_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_five, game=self.game, zone_type='line', owner_player=self.player2)

        duplicate_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate_five, game=self.game, zone_type='deck', position_in_zone=1)

        extra_number = CardDefinition.objects.create(card_name='6', value=6, effect_type='number', effect_payload='')
        extra_instance = CardInstance.objects.create(card_definition=extra_number, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=extra_instance, game=self.game, zone_type='deck', position_in_zone=2)

        view = GameViewSet.as_view({'post': 'flip_three'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['bust'])
        self.assertEqual(len(response.data['drawn_cards']), 1)
        target_membership = GamePlayer.objects.get(game=self.game, player=self.player2)
        self.assertTrue(target_membership.is_busted)

    # FR-25 / US-R23 traceability.
    def test_flip_three_resolves_deferred_freeze_after_draw_sequence(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        freeze_def = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')
        num_one = CardDefinition.objects.create(card_name='1', value=1, effect_type='number', effect_payload='')
        num_two = CardDefinition.objects.create(card_name='2', value=2, effect_type='number', effect_payload='')

        freeze_instance = CardInstance.objects.create(card_definition=freeze_def, game=self.game, deck=deck)
        one_instance = CardInstance.objects.create(card_definition=num_one, game=self.game, deck=deck)
        two_instance = CardInstance.objects.create(card_definition=num_two, game=self.game, deck=deck)

        CardLocation.objects.create(card_instance=freeze_instance, game=self.game, zone_type='deck', position_in_zone=1)
        CardLocation.objects.create(card_instance=one_instance, game=self.game, zone_type='deck', position_in_zone=2)
        CardLocation.objects.create(card_instance=two_instance, game=self.game, zone_type='deck', position_in_zone=3)

        view = GameViewSet.as_view({'post': 'flip_three'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deferred_action'], 'freeze')
        self.assertEqual(len(response.data['drawn_cards']), 3)
        self.assertFalse(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

    def test_action_response_has_consistent_payload_shape(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'stay'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/stay/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action_type'], 'stay')
        self.assertEqual(response.data['actor_player_id'], self.player1.id)
        self.assertIn('outcome', response.data)
        self.assertIn('state', response.data)
        self.assertIn('next_turn_player_id', response.data)

    # FR-08 / US-R06 traceability.
    def test_busted_player_scores_zero_in_round_summary(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        turn = Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        first_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        duplicate_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)

        CardLocation.objects.create(card_instance=first_five, game=self.game, zone_type='line', owner_player=self.player1)
        CardLocation.objects.create(card_instance=duplicate_five, game=self.game, zone_type='deck')

        hit_result = handle_hit(round_obj, self.player1)
        self.assertTrue(hit_result['bust'])

        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        self.assertTrue(gp1.is_busted)

        stay_result = handle_stay(round_obj, self.player2)
        self.assertTrue(stay_result['round_ended'])
        score_by_player = {entry['player_id']: entry['score'] for entry in stay_result['round_summary']}
        self.assertEqual(score_by_player[self.player1.id], 0)

    # FR-11 / US-R10 traceability.
    def test_flip_seven_bonus_applies_only_to_round_winner(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in range(0, 7):
            definition = CardDefinition.objects.create(card_name=f'p1-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player1)

        for value in range(0, 7):
            definition = CardDefinition.objects.create(card_name=f'p2-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player2)

        round_obj.winner_player = self.player1
        round_obj.save(update_fields=['winner_player'])

        result = finalize_round(round_obj)
        score_by_player = {entry['player_id']: entry['score'] for entry in result['round_summary']}

        base = sum(range(0, 7))
        self.assertEqual(score_by_player[self.player1.id], base + 15)
        self.assertEqual(score_by_player[self.player2.id], base)

    # FR-31 / US-R26 traceability.
    def test_finalize_round_marks_game_finished_on_cumulative_score(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        gp1.final_score = 199
        gp1.save(update_fields=['final_score'])

        one_card = CardDefinition.objects.create(card_name='one-point', value=1, effect_type='number', effect_payload='')
        one_instance = CardInstance.objects.create(card_definition=one_card, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=one_instance, game=self.game, zone_type='line', owner_player=self.player1)

        finalize_round(round_obj)
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, 'finished')

    def test_deterministic_deck_order_with_test_seed(self):
        game_one = Game.objects.create(game_code='FLIPSEED1', created_by=self.player1)
        game_two = Game.objects.create(game_code='FLIPSEED2', created_by=self.player1)
        GamePlayer.objects.create(game=game_one, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game_two, player=self.player1, seat_number=1)

        with patch.dict('os.environ', {'FLIP7_TEST_SEED': 'fixed-seed'}):
            start_round(game_one)
            start_round(game_two)

        cards_one = [loc.card_instance.card_definition.card_name for loc in CardLocation.objects.filter(game=game_one, owner_player=self.player1, zone_type='line').order_by('position_in_zone')]
        cards_two = [loc.card_instance.card_definition.card_name for loc in CardLocation.objects.filter(game=game_two, owner_player=self.player1, zone_type='line').order_by('position_in_zone')]
        self.assertEqual(cards_one, cards_two)

    def test_error_response_shape_is_consistent_for_action_validation(self):
        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/hit/',
            {},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('error_code', response.data)
        self.assertIn('details', response.data)

    def test_results_endpoint_returns_standings(self):
        view = GameViewSet.as_view({'get': 'results'})
        request = APIRequestFactory().get(f'/api/games/{self.game.id}/results/')
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['game_id'], self.game.id)
        self.assertIn('standings', response.data)

    # FR-31 / US-R26 traceability.
    def test_results_endpoint_winner_is_highest_total_score(self):
        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        gp2 = GamePlayer.objects.get(game=self.game, player=self.player2)
        gp1.final_score = 35
        gp2.final_score = 42
        gp1.save(update_fields=['final_score'])
        gp2.save(update_fields=['final_score'])

        view = GameViewSet.as_view({'get': 'results'})
        request = APIRequestFactory().get(f'/api/games/{self.game.id}/results/')
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['winner']['player_id'], self.player2.id)
        self.assertGreater(response.data['winner']['total_score'], response.data['standings'][1]['total_score'])

    # FR-31 / US-R26 traceability.
    def test_finalize_round_persists_rankings_in_game_results(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        gp2 = GamePlayer.objects.get(game=self.game, player=self.player2)
        gp1.final_score = 30
        gp2.final_score = 60
        gp1.save(update_fields=['final_score'])
        gp2.save(update_fields=['final_score'])

        finalize_round(round_obj)

        results = list(GameResult.objects.filter(game=self.game).order_by('ranking'))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].player_id, self.player2.id)
        self.assertEqual(results[0].ranking, 1)
        self.assertEqual(results[1].player_id, self.player1.id)
        gp1.refresh_from_db()
        gp2.refresh_from_db()
        self.assertEqual(gp2.ranking, 1)
        self.assertEqual(gp1.ranking, 2)

    # FR-14 / US-R13 traceability.
    def test_round_score_calculate_applies_modifiers_and_flip_seven_bonus(self):
        round_obj = Round.objects.create(game=self.game, round_number=1, winner_player=self.player1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in range(0, 7):
            definition = CardDefinition.objects.create(card_name=f'n-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player1)

        x2 = CardDefinition.objects.create(card_name='x2', value=None, effect_type='modifier', effect_payload='x2')
        plus4 = CardDefinition.objects.create(card_name='+4', value=None, effect_type='modifier', effect_payload='+4')
        x2_instance = CardInstance.objects.create(card_definition=x2, game=self.game, deck=deck)
        plus4_instance = CardInstance.objects.create(card_definition=plus4, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=x2_instance, game=self.game, zone_type='line', owner_player=self.player1)
        CardLocation.objects.create(card_instance=plus4_instance, game=self.game, zone_type='line', owner_player=self.player1)

        view = RoundViewSet.as_view({'post': 'score_calculate'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/score/calculate/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number_subtotal'], 21)
        self.assertEqual(response.data['multiplier'], 2)
        self.assertEqual(response.data['modifier_total'], 4)
        self.assertEqual(response.data['bonus_points'], 15)
        self.assertEqual(response.data['final_score'], 61)

    def test_score_apply_adds_round_score_to_total(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'score_apply'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/score/apply/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['player_id'], self.player1.id)
        self.assertEqual(response.data['new_total'], response.data['applied_score'])
        self.assertEqual(
            GamePlayer.objects.get(game=self.game, player=self.player1).final_score,
            response.data['new_total'],
        )

    def test_rules_validate_hit_returns_valid_true_on_current_turn(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'rules_validate'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/rules/validate/',
            {'action_type': 'hit', 'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])

    def test_rules_resolve_hit_executes_action(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'rules_resolve'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/rules/resolve/',
            {'action_type': 'hit', 'payload': {'player_id': self.player1.id}},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action_type'], 'hit')

    def test_round_score_calculate_returns_breakdown(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'score_calculate'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/score/calculate/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('number_subtotal', response.data)
        self.assertIn('final_score', response.data)

    def test_round_bust_endpoint_marks_player_busted(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'bust'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/actions/bust/',
            {'player_id': self.player1.id, 'reason': 'duplicate'},
            format='json',
        )
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        membership = GamePlayer.objects.get(game=self.game, player=self.player1)
        self.assertTrue(membership.is_busted)

    # FR-29 / US-R25 traceability.
    def test_round_end_check_endpoint_returns_status(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'end_check'})
        request = APIRequestFactory().post(f'/api/rounds/{round_obj.id}/end-check/', {}, format='json')
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('round_ended', response.data)

    # FR-19 / US-R17 traceability.
    def test_round_end_check_discards_second_chance_cards_when_round_ends(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        second_chance = CardDefinition.objects.create(card_name='Second Chance', value=None, effect_type='action', effect_payload='second_chance')
        second_chance_instance = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=second_chance_instance, game=self.game, zone_type='line', owner_player=self.player1)

        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        gp2 = GamePlayer.objects.get(game=self.game, player=self.player2)
        gp1.is_active = False
        gp2.is_active = False
        gp1.save(update_fields=['is_active'])
        gp2.save(update_fields=['is_active'])

        view = RoundViewSet.as_view({'post': 'end_check'})
        request = APIRequestFactory().post(f'/api/rounds/{round_obj.id}/end-check/', {}, format='json')
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['round_ended'])
        latest_location = CardLocation.objects.filter(card_instance=second_chance_instance).order_by('-id').first()
        self.assertEqual(latest_location.zone_type, 'discard')

    # FR-29 / US-R25 traceability.
    def test_round_end_check_returns_round_continues_when_active_players_remain(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'end_check'})
        request = APIRequestFactory().post(f'/api/rounds/{round_obj.id}/end-check/', {}, format='json')
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['round_ended'])
        self.assertEqual(response.data['reason'], 'round_continues')

    # FR-11 / US-R10 and FR-29 / US-R25 traceability.
    def test_flip_seven_endpoint_awards_bonus_and_ends_round(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in range(0, 7):
            definition = CardDefinition.objects.create(card_name=f'p1-u-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player1)

        view = RoundViewSet.as_view({'post': 'flip_seven'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/actions/flip-seven/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['flip_seven'])
        round_obj.refresh_from_db()
        self.assertEqual(round_obj.winner_player_id, self.player1.id)
        self.assertIsNotNone(round_obj.ended_at)

    def test_create_player_rejects_duplicate_username(self):
        view = PlayerViewSet.as_view({'post': 'create'})
        request = APIRequestFactory().post('/api/players/', {'username': 'alice', 'display_name': 'Alice'}, format='json')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_player_rejects_missing_username(self):
        view = PlayerViewSet.as_view({'post': 'create'})
        request = APIRequestFactory().post('/api/players/', {'display_name': 'Nameless'}, format='json')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_missing_player_returns_404(self):
        view = PlayerViewSet.as_view({'get': 'retrieve'})
        request = APIRequestFactory().get('/api/players/99999/')
        response = view(request, pk=99999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_game_rejects_invalid_creator(self):
        view = GameViewSet.as_view({'post': 'create'})
        request = APIRequestFactory().post('/api/games/', {'created_by': 99999}, format='json')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['error_code'], {'validation_error', 'invalid_created_by'})

    def test_join_rejects_duplicate_seat_assignment(self):
        game = Game.objects.create(game_code='FLIPSEAT', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        newcomer = Player.objects.create(username='charlie')

        view = GameViewSet.as_view({'post': 'join'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/join/',
            {'player_id': newcomer.id, 'seat_number': 1},
            format='json',
        )
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'seat_taken')

    def test_db_constraint_rejects_duplicate_seat_number_per_game(self):
        extra_player = Player.objects.create(username='duplicate-seat')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GamePlayer.objects.create(game=self.game, player=extra_player, seat_number=1)

    def test_db_constraint_rejects_non_positive_seat(self):
        extra_player = Player.objects.create(username='seat-zero')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GamePlayer.objects.create(game=self.game, player=extra_player, seat_number=0)

    def test_db_constraint_rejects_line_card_without_owner(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        card_def = CardDefinition.objects.create(card_name='C', value=1, effect_type='number', effect_payload='')
        instance = CardInstance.objects.create(card_definition=card_def, game=self.game, deck=deck)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=None)

    def test_db_constraint_rejects_deck_card_with_owner(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        card_def = CardDefinition.objects.create(card_name='D', value=2, effect_type='number', effect_payload='')
        instance = CardInstance.objects.create(card_definition=card_def, game=self.game, deck=deck)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='deck', owner_player=self.player1)

    def test_join_rejects_finished_game(self):
        game = Game.objects.create(game_code='FLIPDONE', created_by=self.player1, status='finished')
        view = GameViewSet.as_view({'post': 'join'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/join/',
            {'player_id': self.player2.id, 'seat_number': 2},
            format='json',
        )
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_finished')

    def test_start_round_rejects_finished_game(self):
        game = Game.objects.create(game_code='FLIPEND', created_by=self.player1, status='finished')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        view = GameViewSet.as_view({'post': 'start_round'})
        request = APIRequestFactory().post(f'/api/games/{game.id}/start_round/', {}, format='json')
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_finished')

    def test_start_round_rejects_single_player_game(self):
        game = Game.objects.create(game_code='FLIPSOLO', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        view = GameViewSet.as_view({'post': 'start_round'})
        request = APIRequestFactory().post(f'/api/games/{game.id}/start_round/', {}, format='json')
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'not_enough_players')

    def test_join_rejects_full_game(self):
        game = Game.objects.create(game_code='FLIPFULL', created_by=self.player1)
        for seat in range(1, 31):
            player = Player.objects.create(username=f'fullseat{seat}')
            GamePlayer.objects.create(game=game, player=player, seat_number=seat)
        newcomer = Player.objects.create(username='overflow')
        view = GameViewSet.as_view({'post': 'join'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/join/',
            {'player_id': newcomer.id, 'seat_number': 31},
            format='json',
        )
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_full')

    def test_join_rejects_after_round_started(self):
        game = Game.objects.create(game_code='FLIPGO', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        Round.objects.create(game=game, round_number=1)
        newcomer = Player.objects.create(username='latecomer')
        view = GameViewSet.as_view({'post': 'join'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/join/',
            {'player_id': newcomer.id, 'seat_number': 3},
            format='json',
        )
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_already_started')

    def test_close_deletes_game_and_all_data(self):
        game = Game.objects.create(game_code='FLIPCLOSE', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        game_id = game.id
        view = GameViewSet.as_view({'post': 'close'})
        request = APIRequestFactory().post(f'/api/games/{game_id}/close/', {}, format='json')
        response = view(request, pk=game_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(id=game_id).exists())
        self.assertFalse(GamePlayer.objects.filter(game_id=game_id).exists())

    def test_remove_player_detaches_membership_from_pending_game(self):
        game = Game.objects.create(game_code='FLIPRM01', created_by=self.player1)
        p3 = Player.objects.create(username='carol')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        GamePlayer.objects.create(game=game, player=p3, seat_number=3)

        view = GameViewSet.as_view({'post': 'remove_player'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/remove_player/',
            {'player_id': p3.id},
            format='json',
        )
        response = view(request, pk=game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(GamePlayer.objects.filter(game=game, player=p3).exists())
        self.assertEqual(GamePlayer.objects.filter(game=game).count(), 2)
        self.assertTrue(Player.objects.filter(id=p3.id).exists())  # Player record preserved.

    def test_remove_player_rejected_below_minimum(self):
        game = Game.objects.create(game_code='FLIPRM02', created_by=self.player1)
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)

        view = GameViewSet.as_view({'post': 'remove_player'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/remove_player/',
            {'player_id': self.player2.id},
            format='json',
        )
        response = view(request, pk=game.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'not_enough_players')
        self.assertEqual(GamePlayer.objects.filter(game=game).count(), 2)

    def test_remove_player_rejected_after_round_started(self):
        game = Game.objects.create(game_code='FLIPRM03', created_by=self.player1)
        p3 = Player.objects.create(username='carol')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        GamePlayer.objects.create(game=game, player=p3, seat_number=3)
        Round.objects.create(game=game, round_number=1)

        view = GameViewSet.as_view({'post': 'remove_player'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/remove_player/',
            {'player_id': p3.id},
            format='json',
        )
        response = view(request, pk=game.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_already_started')
        self.assertTrue(GamePlayer.objects.filter(game=game, player=p3).exists())

    def test_remove_player_rejected_when_not_in_game(self):
        game = Game.objects.create(game_code='FLIPRM04', created_by=self.player1)
        outsider = Player.objects.create(username='carol')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)

        view = GameViewSet.as_view({'post': 'remove_player'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/remove_player/',
            {'player_id': outsider.id},
            format='json',
        )
        response = view(request, pk=game.id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 'player_not_found')

    def _four_player_round(self):
        game = Game.objects.create(game_code='FLIP4WAY', created_by=self.player1)
        p3 = Player.objects.create(username='carol')
        p4 = Player.objects.create(username='dave')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        GamePlayer.objects.create(game=game, player=self.player2, seat_number=2)
        GamePlayer.objects.create(game=game, player=p3, seat_number=3)
        GamePlayer.objects.create(game=game, player=p4, seat_number=4)
        round_obj = Round.objects.create(game=game, round_number=1)
        return game, round_obj, p3, p4

    def test_bust_advances_to_next_seat_not_back_to_first(self):
        # BUG-01: a middle-seat bust must continue the round, not jump back to seat 1.
        game, round_obj, p3, _p4 = self._four_player_round()
        Turn.objects.create(game=game, round=round_obj, turn_number=1, acting_player=self.player2, action_type='turn')
        deck = Deck.objects.create(game=game, deck_name='Main Deck', deck_type='main')
        five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        existing = CardInstance.objects.create(card_definition=five, game=game, deck=deck)
        CardLocation.objects.create(card_instance=existing, game=game, zone_type='line', owner_player=self.player2, position_in_zone=1)
        duplicate = CardInstance.objects.create(card_definition=five, game=game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate, game=game, zone_type='deck', position_in_zone=1)

        result = handle_hit(round_obj, self.player2)

        self.assertTrue(result['bust'])
        self.assertFalse(result['round_ended'])
        self.assertEqual(result['next_turn_player_id'], p3.id)

    # FR-06 / US-R05 traceability.
    def test_stay_advances_to_next_seat_not_back_to_first(self):
        # BUG-01: staying must also continue by seat order, not reset to seat 1.
        game, round_obj, p3, _p4 = self._four_player_round()
        Turn.objects.create(game=game, round=round_obj, turn_number=1, acting_player=self.player2, action_type='turn')

        result = handle_stay(round_obj, self.player2)

        self.assertFalse(result['round_ended'])
        self.assertEqual(result['next_turn_player_id'], p3.id)

    def test_last_seat_bust_wraps_to_lowest_active_seat(self):
        # BUG-01: after the highest seat, rotation wraps to the lowest still-active seat.
        game, round_obj, _p3, p4 = self._four_player_round()
        Turn.objects.create(game=game, round=round_obj, turn_number=1, acting_player=p4, action_type='turn')
        deck = Deck.objects.create(game=game, deck_name='Main Deck', deck_type='main')
        five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        existing = CardInstance.objects.create(card_definition=five, game=game, deck=deck)
        CardLocation.objects.create(card_instance=existing, game=game, zone_type='line', owner_player=p4, position_in_zone=1)
        duplicate = CardInstance.objects.create(card_definition=five, game=game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate, game=game, zone_type='deck', position_in_zone=1)

        result = handle_hit(round_obj, p4)

        self.assertTrue(result['bust'])
        self.assertFalse(result['round_ended'])
        self.assertEqual(result['next_turn_player_id'], self.player1.id)


        game = Game.objects.create(game_code='FLIPSTOP', created_by=self.player1, status='finished')
        GamePlayer.objects.create(game=game, player=self.player1, seat_number=1)
        round_obj = Round.objects.create(game=game, round_number=1)
        Turn.objects.create(game=game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')

        view = GameViewSet.as_view({'post': 'hit'})
        request = APIRequestFactory().post(
            f'/api/games/{game.id}/hit/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=game.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'game_finished')

    def test_flip_seven_endpoint_rejects_when_condition_not_met(self):
        round_obj, _ = start_round(self.game)
        view = RoundViewSet.as_view({'post': 'flip_seven'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/actions/flip-seven/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'flip_seven_condition_not_met')

    def test_bust_endpoint_rejects_already_busted_player(self):
        round_obj, _ = start_round(self.game)
        membership = GamePlayer.objects.get(game=self.game, player=self.player1)
        membership.is_busted = True
        membership.is_active = False
        membership.save(update_fields=['is_busted', 'is_active'])

        view = RoundViewSet.as_view({'post': 'bust'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/actions/bust/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'already_busted')

    def test_score_apply_is_idempotent_after_round_end(self):
        round_obj, _ = start_round(self.game)
        round_obj.ended_at = round_obj.started_at
        round_obj.save(update_fields=['ended_at'])
        membership = GamePlayer.objects.get(game=self.game, player=self.player1)
        membership.final_score = 12
        membership.save(update_fields=['final_score'])

        view = RoundViewSet.as_view({'post': 'score_apply'})
        request = APIRequestFactory().post(
            f'/api/rounds/{round_obj.id}/score/apply/',
            {'player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=round_obj.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['already_applied'])
        self.assertEqual(response.data['new_total'], 12)

    def test_flip_three_self_bust_advances_turn_to_opponent(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        existing = CardInstance.objects.create(card_definition=five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=1)
        duplicate = CardInstance.objects.create(card_definition=five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate, game=self.game, zone_type='deck', position_in_zone=1)

        view = GameViewSet.as_view({'post': 'flip_three'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/flip_three/',
            {'player_id': self.player1.id, 'target_player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['bust'])
        self.assertFalse(response.data['round_ended'])
        self.assertEqual(response.data['next_turn_player_id'], self.player2.id)
        self.assertFalse(GamePlayer.objects.get(game=self.game, player=self.player1).is_active)
        self.assertTrue(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

    # FR-26 / US-R24 traceability.
    def test_flip_three_last_player_bust_finalizes_round(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        GamePlayer.objects.filter(game=self.game, player=self.player1).update(is_active=False)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        existing = CardInstance.objects.create(card_definition=five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing, game=self.game, zone_type='line', owner_player=self.player2, position_in_zone=1)
        duplicate = CardInstance.objects.create(card_definition=five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=duplicate, game=self.game, zone_type='deck', position_in_zone=1)

        result = handle_flip_three(round_obj, self.player2, self.player2)

        self.assertTrue(result['bust'])
        self.assertTrue(result['round_ended'])
        round_obj.refresh_from_db()
        self.assertIsNotNone(round_obj.ended_at)

    # FR-27 / US-R20 traceability.
    def test_freeze_discards_used_action_card_from_line(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        freeze_def = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')
        freeze_instance = CardInstance.objects.create(card_definition=freeze_def, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=freeze_instance, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=1)

        handle_freeze(round_obj, self.player1, self.player2)

        self.assertFalse(
            CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line', card_instance=freeze_instance).exists()
        )
        self.assertTrue(
            CardLocation.objects.filter(game=self.game, zone_type='discard', card_instance=freeze_instance).exists()
        )

    # FR-04 / US-R29 and FR-30 / US-R28 traceability.
    def test_line_cleared_and_deck_persists_between_rounds(self):
        round_obj, _ = start_round(self.game)
        self.assertEqual(CardInstance.objects.filter(game=self.game).count(), 94)

        finalize_round(round_obj)
        self.assertEqual(CardLocation.objects.filter(game=self.game, zone_type='line').count(), 0)

        start_round(self.game)
        self.assertEqual(CardInstance.objects.filter(game=self.game).count(), 94)
        for game_player in self.game.game_players.all():
            self.assertEqual(
                CardLocation.objects.filter(game=self.game, zone_type='line', owner_player=game_player.player).count(),
                1,
            )

    # FR-04 / US-R29 traceability.
    def test_draw_reshuffles_discard_when_deck_empty(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        number = CardDefinition.objects.create(card_name='7', value=7, effect_type='number', effect_payload='')
        instance = CardInstance.objects.create(card_definition=number, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='discard', position_in_zone=1)

        drawn = draw_card_for_player(self.game, self.player1)

        self.assertIsNotNone(drawn)
        self.assertEqual(drawn.id, instance.id)

    def test_fr01_us_r01_deck_definition_counts_match_composition(self):
        start_round(self.game)

        counts = {}
        for card_name in CardInstance.objects.filter(game=self.game).values_list('card_definition__card_name', flat=True):
            counts[card_name] = counts.get(card_name, 0) + 1

        self.assertEqual(sum(counts.values()), 94)
        self.assertEqual(counts, DECK_COMPOSITION)

    def test_fr02_us_r02_plus8_and_plus10_are_reachable_in_deck(self):
        start_round(self.game)

        names = list(CardInstance.objects.filter(game=self.game).values_list('card_definition__card_name', flat=True))
        self.assertIn('+8', names)
        self.assertIn('+10', names)

    def test_fr03_us_r03_action_card_frequency_is_three_each(self):
        start_round(self.game)

        action_counts = {
            'Freeze': CardInstance.objects.filter(game=self.game, card_definition__card_name='Freeze').count(),
            'Flip Three': CardInstance.objects.filter(game=self.game, card_definition__card_name='Flip Three').count(),
            'Second Chance': CardInstance.objects.filter(game=self.game, card_definition__card_name='Second Chance').count(),
        }
        self.assertEqual(action_counts, {'Freeze': 3, 'Flip Three': 3, 'Second Chance': 3})

    def test_fr09_us_r07_modifier_draw_does_not_bust(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        plus_eight = CardDefinition.objects.create(card_name='+8', value=None, effect_type='modifier', effect_payload='+8')

        existing_number = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_number, game=self.game, zone_type='line', owner_player=self.player1)

        modifier_draw = CardInstance.objects.create(card_definition=plus_eight, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=modifier_draw, game=self.game, zone_type='deck')

        result = handle_hit(round_obj, self.player1)
        self.assertFalse(result['bust'])

    def test_fr09_us_r07_action_draw_does_not_bust(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        freeze = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')

        existing_number = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_number, game=self.game, zone_type='line', owner_player=self.player1)

        action_draw = CardInstance.objects.create(card_definition=freeze, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=action_draw, game=self.game, zone_type='deck')

        result = handle_hit(round_obj, self.player1)
        self.assertFalse(result['bust'])

    def test_fr12_us_r11_only_numbers_count_toward_flip7(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in [1, 2, 3, 4, 5, 6]:
            definition = CardDefinition.objects.create(card_name=f'n-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player1)

        freeze = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')
        modifier = CardDefinition.objects.create(card_name='+2', value=None, effect_type='modifier', effect_payload='+2')
        freeze_instance = CardInstance.objects.create(card_definition=freeze, game=self.game, deck=deck)
        modifier_instance = CardInstance.objects.create(card_definition=modifier, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=freeze_instance, game=self.game, zone_type='line', owner_player=self.player1)
        CardLocation.objects.create(card_instance=modifier_instance, game=self.game, zone_type='line', owner_player=self.player1)

        _score, unique_count = calculate_round_score(self.game, self.player1)
        self.assertEqual(unique_count, 6)

    def test_fr13_us_r12_zero_counts_as_unique_and_scores_zero(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        zero = CardDefinition.objects.create(card_name='0', value=0, effect_type='number', effect_payload='')
        zero_instance = CardInstance.objects.create(card_definition=zero, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=zero_instance, game=self.game, zone_type='line', owner_player=self.player1)

        score, unique_count = calculate_round_score(self.game, self.player1)
        self.assertEqual(score, 0)
        self.assertEqual(unique_count, 1)

    def test_fr15_us_r14_x2_without_numbers_scores_zero(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        x2 = CardDefinition.objects.create(card_name='x2', value=None, effect_type='modifier', effect_payload='x2')
        x2_instance = CardInstance.objects.create(card_definition=x2, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=x2_instance, game=self.game, zone_type='line', owner_player=self.player1)

        breakdown = calculate_round_score_breakdown(self.game, self.player1)
        self.assertEqual(breakdown['final_score'], 0)

    def test_fr16_us_r27_bust_scores_zero_but_keeps_previous_total(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        gp1 = GamePlayer.objects.get(game=self.game, player=self.player1)
        gp1.final_score = 25
        gp1.save(update_fields=['final_score'])

        number_five = CardDefinition.objects.create(card_name='5', value=5, effect_type='number', effect_payload='')
        first_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        second_five = CardInstance.objects.create(card_definition=number_five, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=first_five, game=self.game, zone_type='line', owner_player=self.player1)
        CardLocation.objects.create(card_instance=second_five, game=self.game, zone_type='deck')

        hit_result = handle_hit(round_obj, self.player1)
        self.assertTrue(hit_result['bust'])

        # End round by making the second player stay.
        handle_stay(round_obj, self.player2)

        gp1.refresh_from_db()
        self.assertEqual(gp1.final_score, 25)

    def test_fr18_us_r16_second_chance_discards_when_no_eligible_player(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')
        second_chance = CardDefinition.objects.create(card_name='Second Chance', value=None, effect_type='action', effect_payload='second_chance')

        # Both active players already hold one Second Chance.
        existing_p1 = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        existing_p2 = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=existing_p1, game=self.game, zone_type='line', owner_player=self.player1)
        CardLocation.objects.create(card_instance=existing_p2, game=self.game, zone_type='line', owner_player=self.player2)

        drawn_second_chance = CardInstance.objects.create(card_definition=second_chance, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=drawn_second_chance, game=self.game, zone_type='line', owner_player=self.player1)

        result = resolve_second_chance_draw(self.game, self.player1, drawn_second_chance)
        self.assertFalse(result['kept'])
        self.assertIsNone(result['passed_to'])
        latest_location = CardLocation.objects.filter(card_instance=drawn_second_chance).order_by('-id').first()
        self.assertEqual(latest_location.zone_type, 'discard')

    def test_fr20_us_r18_freeze_banks_target_score_and_deactivates_target(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        num = CardDefinition.objects.create(card_name='7', value=7, effect_type='number', effect_payload='')
        mod = CardDefinition.objects.create(card_name='+4', value=None, effect_type='modifier', effect_payload='+4')
        n_instance = CardInstance.objects.create(card_definition=num, game=self.game, deck=deck)
        m_instance = CardInstance.objects.create(card_definition=mod, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=n_instance, game=self.game, zone_type='line', owner_player=self.player2)
        CardLocation.objects.create(card_instance=m_instance, game=self.game, zone_type='line', owner_player=self.player2)

        expected_score, _ = calculate_round_score(self.game, self.player2)
        result = handle_freeze(round_obj, self.player1, self.player2)

        self.assertEqual(result['frozen_score'], expected_score)
        self.assertFalse(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

    def test_fr21_us_r20_freeze_allows_self_target_when_active(self):
        start_round(self.game)
        view = GameViewSet.as_view({'post': 'freeze'})
        request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player1.id},
            format='json',
        )
        response = view(request, pk=self.game.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fr22_us_r19_lone_active_player_must_target_self(self):
        start_round(self.game)
        GamePlayer.objects.filter(game=self.game, player=self.player2).update(is_active=False)

        view = GameViewSet.as_view({'post': 'freeze'})

        invalid_request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player2.id},
            format='json',
        )
        invalid_response = view(invalid_request, pk=self.game.id)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

        valid_request = APIRequestFactory().post(
            f'/api/games/{self.game.id}/freeze/',
            {'player_id': self.player1.id, 'target_player_id': self.player1.id},
            format='json',
        )
        valid_response = view(valid_request, pk=self.game.id)
        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)

    def test_fr24_us_r22_flip_three_stops_when_target_hits_flip_seven(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        for value in [1, 2, 3, 4, 5, 6]:
            definition = CardDefinition.objects.create(card_name=f'existing-{value}', value=value, effect_type='number', effect_payload='')
            instance = CardInstance.objects.create(card_definition=definition, game=self.game, deck=deck)
            CardLocation.objects.create(card_instance=instance, game=self.game, zone_type='line', owner_player=self.player2)

        seven = CardDefinition.objects.create(card_name='7', value=7, effect_type='number', effect_payload='')
        nine = CardDefinition.objects.create(card_name='9', value=9, effect_type='number', effect_payload='')
        seven_instance = CardInstance.objects.create(card_definition=seven, game=self.game, deck=deck)
        nine_instance = CardInstance.objects.create(card_definition=nine, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=seven_instance, game=self.game, zone_type='deck', position_in_zone=1)
        CardLocation.objects.create(card_instance=nine_instance, game=self.game, zone_type='deck', position_in_zone=2)

        result = handle_flip_three(round_obj, self.player1, self.player2)
        self.assertTrue(result['flip_seven'])
        self.assertTrue(result['round_ended'])
        self.assertEqual(len(result['drawn_cards']), 1)

    def test_fr27_us_r20_hit_drawn_action_card_is_held_until_holder_turn_resolution(self):
        round_obj = Round.objects.create(game=self.game, round_number=1)
        Turn.objects.create(game=self.game, round=round_obj, turn_number=1, acting_player=self.player1, action_type='turn')
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        freeze = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')
        number = CardDefinition.objects.create(card_name='4', value=4, effect_type='number', effect_payload='')
        line_number = CardInstance.objects.create(card_definition=number, game=self.game, deck=deck)
        freeze_draw = CardInstance.objects.create(card_definition=freeze, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=line_number, game=self.game, zone_type='line', owner_player=self.player1, position_in_zone=1)
        CardLocation.objects.create(card_instance=freeze_draw, game=self.game, zone_type='deck', position_in_zone=1)

        hit_result = handle_hit(round_obj, self.player1)
        self.assertFalse(hit_result['bust'])
        self.assertEqual(hit_result['next_turn_player_id'], self.player2.id)
        self.assertTrue(
            CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line', card_instance=freeze_draw).exists()
        )
        self.assertTrue(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

        stay_result = handle_stay(round_obj, self.player2)
        self.assertEqual(stay_result['next_turn_player_id'], self.player1.id)

        resolve_result = handle_freeze(round_obj, self.player1, self.player2)
        self.assertIn('target_player_id', resolve_result)
        self.assertFalse(
            CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line', card_instance=freeze_draw).exists()
        )

    def test_fr28_us_r28_opening_hand_action_card_is_held_until_resolved(self):
        deck = Deck.objects.create(game=self.game, deck_name='Main Deck', deck_type='main')

        freeze = CardDefinition.objects.create(card_name='Freeze', value=None, effect_type='action', effect_payload='freeze')
        number = CardDefinition.objects.create(card_name='2', value=2, effect_type='number', effect_payload='')
        freeze_instance = CardInstance.objects.create(card_definition=freeze, game=self.game, deck=deck)
        other_opening = CardInstance.objects.create(card_definition=number, game=self.game, deck=deck)
        CardLocation.objects.create(card_instance=freeze_instance, game=self.game, zone_type='deck', position_in_zone=1)
        CardLocation.objects.create(card_instance=other_opening, game=self.game, zone_type='deck', position_in_zone=2)

        round_obj, turn_obj = start_round(self.game)

        self.assertEqual(turn_obj.acting_player_id, self.player1.id)
        self.assertTrue(
            CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line', card_instance=freeze_instance).exists()
        )
        self.assertTrue(GamePlayer.objects.get(game=self.game, player=self.player2).is_active)

        response = handle_freeze(round_obj, self.player1, self.player2)
        self.assertIn('target_player_id', response)
        self.assertFalse(
            CardLocation.objects.filter(game=self.game, owner_player=self.player1, zone_type='line', card_instance=freeze_instance).exists()
        )
