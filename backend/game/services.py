import hashlib
import os
import random
from django.utils import timezone
from .models import CardDefinition, CardInstance, CardLocation, Deck, Game, GamePlayer, GameResult, Round, Turn


# Official Flip 7 deck composition (94 cards total): numbers 0-12 (N copies of N, one 0),
# one of each score modifier (+2,+4,+6,+8,+10,x2), and three of each action card.
DECK_COMPOSITION = {
    "0": 1,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "11": 11,
    "12": 12,
    "+2": 1,
    "+4": 1,
    "+6": 1,
    "+8": 1,
    "+10": 1,
    "x2": 1,
    "Freeze": 3,
    "Flip Three": 3,
    "Second Chance": 3,
}


def create_game_code():
    for _ in range(50):
        code = f"FLIP{random.randint(1000, 9999)}"
        if not Game.objects.filter(game_code=code).exists():
            return code
    return f"FLIP{random.randint(100000, 999999)}"


def _get_shuffle_rng():
    seed_text = os.getenv("FLIP7_TEST_SEED")
    if not seed_text:
        return random.Random()
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def seed_card_definitions():
    definitions = [
        {"card_name": "0", "value": 0, "effect_type": "number", "effect_payload": ""},
        {"card_name": "1", "value": 1, "effect_type": "number", "effect_payload": ""},
        {"card_name": "2", "value": 2, "effect_type": "number", "effect_payload": ""},
        {"card_name": "3", "value": 3, "effect_type": "number", "effect_payload": ""},
        {"card_name": "4", "value": 4, "effect_type": "number", "effect_payload": ""},
        {"card_name": "5", "value": 5, "effect_type": "number", "effect_payload": ""},
        {"card_name": "6", "value": 6, "effect_type": "number", "effect_payload": ""},
        {"card_name": "7", "value": 7, "effect_type": "number", "effect_payload": ""},
        {"card_name": "8", "value": 8, "effect_type": "number", "effect_payload": ""},
        {"card_name": "9", "value": 9, "effect_type": "number", "effect_payload": ""},
        {"card_name": "10", "value": 10, "effect_type": "number", "effect_payload": ""},
        {"card_name": "11", "value": 11, "effect_type": "number", "effect_payload": ""},
        {"card_name": "12", "value": 12, "effect_type": "number", "effect_payload": ""},
        {"card_name": "+2", "value": None, "effect_type": "modifier", "effect_payload": "+2"},
        {"card_name": "+4", "value": None, "effect_type": "modifier", "effect_payload": "+4"},
        {"card_name": "+6", "value": None, "effect_type": "modifier", "effect_payload": "+6"},
        {"card_name": "+8", "value": None, "effect_type": "modifier", "effect_payload": "+8"},
        {"card_name": "+10", "value": None, "effect_type": "modifier", "effect_payload": "+10"},
        {"card_name": "x2", "value": None, "effect_type": "modifier", "effect_payload": "x2"},
        {"card_name": "Freeze", "value": None, "effect_type": "action", "effect_payload": "freeze"},
        {"card_name": "Flip Three", "value": None, "effect_type": "action", "effect_payload": "flip_three"},
        {"card_name": "Second Chance", "value": None, "effect_type": "action", "effect_payload": "second_chance"},
    ]
    created = []
    for item in definitions:
        definition, _ = CardDefinition.objects.get_or_create(
            card_name=item["card_name"],
            defaults={
                "value": item["value"],
                "effect_type": item["effect_type"],
                "effect_payload": item["effect_payload"],
                "is_special": item["effect_type"] != "number",
            },
        )
        created.append(definition)
    return created


def ensure_game_deck(game):
    deck, _ = Deck.objects.get_or_create(game=game, deck_type="main", defaults={"deck_name": "Main Deck"})
    if not CardInstance.objects.filter(game=game, deck=deck).exists():
        definitions = seed_card_definitions()
        definition_by_name = {definition.card_name: definition for definition in definitions}

        deck_definitions = []
        for card_name, count in DECK_COMPOSITION.items():
            definition = definition_by_name.get(card_name)
            if definition is None:
                continue
            deck_definitions.extend([definition] * count)

        shuffle_rng = _get_shuffle_rng()
        shuffle_rng.shuffle(deck_definitions)
        for position, definition in enumerate(deck_definitions, start=1):
            card_instance = CardInstance.objects.create(card_definition=definition, game=game, deck=deck)
            CardLocation.objects.create(
                card_instance=card_instance,
                game=game,
                zone_type="deck",
                position_in_zone=position,
                is_face_up=False,
            )
    return deck


def _reshuffle_discard_into_deck(game):
    """Return the discard pile to the deck (used when the deck runs out mid-game)."""
    discard_locations = list(CardLocation.objects.filter(game=game, zone_type="discard"))
    if not discard_locations:
        return False
    shuffle_rng = _get_shuffle_rng()
    shuffle_rng.shuffle(discard_locations)
    for position, location in enumerate(discard_locations, start=1):
        location.zone_type = "deck"
        location.owner_player = None
        location.is_face_up = False
        location.position_in_zone = position
        location.save()
    return True


def draw_card_for_player(game, player):
    deck = ensure_game_deck(game)
    location = (
        CardLocation.objects.filter(game=game, zone_type="deck")
        .select_related("card_instance__card_definition")
        .order_by("position_in_zone", "card_instance__id")
        .first()
    )
    if not location and _reshuffle_discard_into_deck(game):
        location = (
            CardLocation.objects.filter(game=game, zone_type="deck")
            .select_related("card_instance__card_definition")
            .order_by("position_in_zone", "card_instance__id")
            .first()
        )
    if not location:
        return None
    line_position = CardLocation.objects.filter(game=game, zone_type="line", owner_player=player).count() + 1
    location.zone_type = "line"
    location.owner_player = player
    location.is_face_up = True
    location.position_in_zone = line_position
    location.save()
    return location.card_instance


def discard_card_instance(game, card_instance):
    location = CardLocation.objects.filter(game=game, card_instance=card_instance).order_by('-id').first()
    if not location:
        return
    discard_position = CardLocation.objects.filter(game=game, zone_type="discard").count() + 1
    location.zone_type = "discard"
    location.owner_player = None
    location.position_in_zone = discard_position
    location.save()


def discard_action_card_from_line(game, payload, *candidate_players):
    """Discard one line card matching the action payload from the first holder found."""
    for player in candidate_players:
        if player is None:
            continue
        location = (
            CardLocation.objects.filter(
                game=game,
                owner_player=player,
                zone_type="line",
                card_instance__card_definition__effect_payload=payload,
            )
            .order_by("position_in_zone")
            .first()
        )
        if location:
            discard_card_instance(game, location.card_instance)
            return True
    return False


def get_second_chance_locations(game, player):
    return list(
        CardLocation.objects.filter(
            game=game,
            owner_player=player,
            zone_type="line",
            card_instance__card_definition__effect_payload="second_chance",
        ).select_related("card_instance")
    )


def resolve_second_chance_draw(game, player, second_chance_card):
    existing_cards = get_second_chance_locations(game, player)
    if len(existing_cards) <= 1:
        return {"kept": True, "passed_to": None}

    active_players = [
        gp.player for gp in GamePlayer.objects.filter(game=game, is_active=True).order_by("seat_number") if gp.player_id != player.id
    ]
    for candidate in active_players:
        if len(get_second_chance_locations(game, candidate)) == 0:
            location = CardLocation.objects.filter(game=game, card_instance=second_chance_card).order_by('-id').first()
            location.owner_player = candidate
            location.position_in_zone = CardLocation.objects.filter(game=game, zone_type="line", owner_player=candidate).count() + 1
            location.save()
            return {"kept": False, "passed_to": candidate.id}

    discard_card_instance(game, second_chance_card)
    return {"kept": False, "passed_to": None}


def _resolve_duplicate_with_second_chance(game, player, drawn_card):
    definition = drawn_card.card_definition
    if definition.effect_type != "number" or definition.value is None:
        return {"duplicate": False, "saved_by_second_chance": False}

    line_numbers = [
        loc.card_instance.card_definition.value
        for loc in get_player_line(game, player)
        if loc.card_instance.card_definition.effect_type == "number"
    ]
    if line_numbers.count(definition.value) <= 1:
        return {"duplicate": False, "saved_by_second_chance": False}

    second_chance_cards = get_second_chance_locations(game, player)
    if not second_chance_cards:
        return {"duplicate": True, "saved_by_second_chance": False}

    discard_card_instance(game, second_chance_cards[0].card_instance)
    discard_card_instance(game, drawn_card)
    return {"duplicate": True, "saved_by_second_chance": True}


def get_player_line(game, player):
    return list(
        CardLocation.objects.filter(game=game, owner_player=player, zone_type="line")
        .select_related("card_instance__card_definition")
        .order_by("card_instance__id")
    )


def get_active_players(game):
    return list(GamePlayer.objects.filter(game=game, is_active=True).order_by("seat_number"))


def get_next_active_player(game, current_player):
    active_players = get_active_players(game)
    if not active_players:
        return None
    if current_player is None:
        return active_players[0].player

    # Anchor the rotation on the current player's seat using the full roster, so a
    # just-deactivated (busted/stayed) player still advances to the next seat
    # instead of snapping back to the lowest active seat.
    current_membership = GamePlayer.objects.filter(game=game, player=current_player).first()
    if current_membership is None:
        return active_players[0].player

    current_seat = current_membership.seat_number
    next_membership = next(
        (m for m in active_players if m.seat_number > current_seat),
        active_players[0],
    )
    if next_membership.player_id == current_player.id:
        return None
    return next_membership.player


def calculate_round_score(game, player):
    player_cards = get_player_line(game, player)
    number_total = 0
    modifier_total = 0
    multiplier = 1
    unique_numbers = set()
    for location in player_cards:
        definition = location.card_instance.card_definition
        if definition.effect_type == "number" and definition.value is not None:
            number_total += definition.value
            unique_numbers.add(definition.value)
        elif definition.effect_type == "modifier" and definition.effect_payload:
            payload = definition.effect_payload
            if payload.startswith("+"):
                modifier_total += int(payload[1:])
            elif payload.startswith("x"):
                multiplier *= int(payload[1:])
    score = (number_total * multiplier) + modifier_total
    return score, len(unique_numbers)


def calculate_round_score_breakdown(game, player, round_obj=None):
    player_cards = get_player_line(game, player)
    number_subtotal = 0
    modifier_total = 0
    multiplier = 1
    unique_numbers = set()

    for location in player_cards:
        definition = location.card_instance.card_definition
        if definition.effect_type == "number" and definition.value is not None:
            number_subtotal += definition.value
            unique_numbers.add(definition.value)
        elif definition.effect_type == "modifier" and definition.effect_payload:
            payload = definition.effect_payload
            if payload.startswith("+"):
                modifier_total += int(payload[1:])
            elif payload.startswith("x"):
                multiplier *= int(payload[1:])

    base_total = (number_subtotal * multiplier) + modifier_total
    bonus_points = 0
    if round_obj and round_obj.winner_player_id == player.id and len(unique_numbers) >= 7:
        bonus_points = 15

    membership = GamePlayer.objects.filter(game=game, player=player).first()
    if membership and membership.is_busted:
        final_score = 0
    else:
        final_score = base_total + bonus_points

    return {
        "player_id": player.id,
        "number_subtotal": number_subtotal,
        "multiplier": multiplier,
        "modifier_total": modifier_total,
        "bonus_points": bonus_points,
        "unique_numbers": len(unique_numbers),
        "final_score": final_score,
    }


def apply_round_score(game, round_obj, player):
    breakdown = calculate_round_score_breakdown(game, player, round_obj=round_obj)
    membership = GamePlayer.objects.get(game=game, player=player)
    membership.final_score = (membership.final_score or 0) + breakdown["final_score"]
    membership.save(update_fields=["final_score"])
    return {
        "round_id": round_obj.id,
        "player_id": player.id,
        "applied_score": breakdown["final_score"],
        "new_total": membership.final_score,
        "breakdown": breakdown,
    }


def end_round_if_needed(round_obj):
    game = round_obj.game
    if round_obj.ended_at:
        return {"round_ended": True, "round_summary": []}

    if round_obj.winner_player_id:
        summary = finalize_round(round_obj)
        return {"round_ended": True, "reason": "flip_seven", "round_summary": summary["round_summary"]}

    if not get_active_players(game):
        summary = finalize_round(round_obj)
        return {"round_ended": True, "reason": "no_active_players", "round_summary": summary["round_summary"]}

    return {"round_ended": False, "reason": "round_continues"}


def _build_action_response(game, round_obj, action_type, actor_player, outcome, target_player=None, next_turn=None):
    payload = {
        "game_id": game.id,
        "round_id": round_obj.id,
        "action_type": action_type,
        "actor_player_id": actor_player.id if actor_player else None,
        "target_player_id": target_player.id if target_player else None,
        "next_turn_player_id": next_turn.acting_player_id if next_turn else None,
        "outcome": outcome,
        "state": build_game_state(game),
    }
    payload.update(outcome)
    return payload


def finalize_round(round_obj):
    game = round_obj.game
    round_obj.ended_at = timezone.now()
    round_obj.save()
    total_scores = {}
    round_summary = []
    flip_seven_winner_id = round_obj.winner_player_id
    for game_player in game.game_players.all():
        score, unique_count = calculate_round_score(game, game_player.player)
        if game_player.is_busted:
            score = 0
        elif flip_seven_winner_id and game_player.player_id == flip_seven_winner_id and unique_count >= 7:
            score += 15
        total_scores[game_player.player_id] = score
        game_player.final_score = (game_player.final_score or 0) + score
        game_player.save()
        round_summary.append({
            "player_id": game_player.player_id,
            "username": game_player.player.username,
            "score": score,
            "total_score": game_player.final_score,
        })
    game_finished = any((game_player.final_score or 0) >= game.target_score for game_player in game.game_players.all())
    game.status = "finished" if game_finished else "active"
    game.save()

    ranked_memberships = list(game.game_players.select_related("player").order_by("-final_score", "seat_number"))
    for idx, membership in enumerate(ranked_memberships, start=1):
        membership.ranking = idx
        membership.save(update_fields=["ranking"])
        GameResult.objects.update_or_create(
            game=game,
            player=membership.player,
            defaults={
                "score": membership.final_score or 0,
                "ranking": idx,
                "is_winner": bool(game_finished and idx == 1),
            },
        )

    line_locations = CardLocation.objects.filter(
        game=game,
        zone_type="line",
    )
    for location in line_locations:
        location.zone_type = "discard"
        location.owner_player = None
        location.save()

    return {"scores": total_scores, "round_summary": round_summary}


def start_round(game):
    game.status = "active"
    game.started_at = timezone.now()
    game.save()
    round_obj = Round.objects.create(game=game, round_number=game.rounds.count() + 1)
    ensure_game_deck(game)
    for game_player in game.game_players.order_by("seat_number"):
        game_player.is_active = True
        game_player.is_busted = False
        game_player.save(update_fields=["is_active", "is_busted"])
        draw_card_for_player(game, game_player.player)
    first_player = game.game_players.order_by("seat_number").first()
    turn = Turn.objects.create(game=game, round=round_obj, turn_number=1, acting_player=first_player.player, action_type="turn")
    return round_obj, turn


def handle_hit(round_obj, player):
    game = round_obj.game
    drawn_card = draw_card_for_player(game, player)
    if not drawn_card:
        score = calculate_round_score(game, player)[0]
        outcome = {"bust": False, "flip_seven": False, "score": score, "message": "Deck is empty"}
        return _build_action_response(game, round_obj, "hit", player, outcome)

    if drawn_card.card_definition.effect_payload == "second_chance":
        resolve_second_chance_draw(game, player, drawn_card)

    duplicate_result = _resolve_duplicate_with_second_chance(game, player, drawn_card)
    if duplicate_result["duplicate"] and not duplicate_result["saved_by_second_chance"]:
        game_player = GamePlayer.objects.get(game=game, player=player)
        game_player.is_active = False
        game_player.is_busted = True
        game_player.save(update_fields=["is_active", "is_busted"])
        if not get_active_players(game):
            summary = finalize_round(round_obj)
            outcome = {
                "bust": True,
                "flip_seven": False,
                "score": 0,
                "second_chance_used": False,
                "round_ended": True,
                "round_summary": summary["round_summary"],
            }
            return _build_action_response(game, round_obj, "hit", player, outcome)
        next_player = get_next_active_player(game, player)
        turn = None
        if next_player is not None:
            turn = Turn.objects.create(game=game, round=round_obj, turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1, acting_player=next_player, action_type="turn")
        outcome = {"bust": True, "flip_seven": False, "score": 0, "second_chance_used": False, "round_ended": False}
        return _build_action_response(game, round_obj, "hit", player, outcome, next_turn=turn)

    score, unique_count = calculate_round_score(game, player)
    if unique_count >= 7:
        round_obj.winner_player = player
        round_obj.save(update_fields=["winner_player"])
        summary = finalize_round(round_obj)
        outcome = {"bust": False, "flip_seven": True, "score": score + 15, "round_ended": True, "round_summary": summary["round_summary"]}
        return _build_action_response(game, round_obj, "hit", player, outcome)

    next_player = get_next_active_player(game, player)
    turn = None
    if next_player is not None:
        turn = Turn.objects.create(game=game, round=round_obj, turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1, acting_player=next_player, action_type="turn")
    outcome = {
        "bust": False,
        "flip_seven": False,
        "score": score,
        "second_chance_used": duplicate_result["saved_by_second_chance"],
    }
    return _build_action_response(game, round_obj, "hit", player, outcome, next_turn=turn)


def handle_stay(round_obj, player):
    game = round_obj.game
    game_player = GamePlayer.objects.get(game=game, player=player)
    game_player.is_active = False
    game_player.save(update_fields=["is_active"])
    if not get_active_players(game):
        summary = finalize_round(round_obj)
        outcome = {"round_ended": True, "message": "No active players remain", "round_summary": summary["round_summary"]}
        return _build_action_response(game, round_obj, "stay", player, outcome)
    next_player = get_next_active_player(game, player)
    turn = None
    if next_player is not None:
        turn = Turn.objects.create(game=game, round=round_obj, turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1, acting_player=next_player, action_type="turn")
    outcome = {"round_ended": False}
    return _build_action_response(game, round_obj, "stay", player, outcome, next_turn=turn)


def handle_freeze(round_obj, acting_player, target_player):
    game = round_obj.game

    discard_action_card_from_line(game, "freeze", acting_player, target_player)

    target_membership = GamePlayer.objects.get(game=game, player=target_player)
    target_membership.is_active = False
    target_membership.save(update_fields=["is_active"])

    frozen_score, _ = calculate_round_score(game, target_player)

    if not get_active_players(game):
        summary = finalize_round(round_obj)
        outcome = {
            "round_ended": True,
            "target_player_id": target_player.id,
            "frozen_score": frozen_score,
            "round_summary": summary["round_summary"],
        }
        return _build_action_response(game, round_obj, "freeze", acting_player, outcome, target_player=target_player)

    next_player = get_next_active_player(game, acting_player)
    turn = None
    if next_player is not None:
        turn = Turn.objects.create(
            game=game,
            round=round_obj,
            turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1,
            acting_player=next_player,
            action_type="freeze",
        )

    outcome = {
        "round_ended": False,
        "target_player_id": target_player.id,
        "frozen_score": frozen_score,
    }
    return _build_action_response(game, round_obj, "freeze", acting_player, outcome, target_player=target_player, next_turn=turn)


def handle_flip_three(round_obj, acting_player, target_player, depth=0):
    game = round_obj.game
    if depth > 3:
        outcome = {"round_ended": False, "target_player_id": target_player.id, "drawn_cards": [], "message": "Flip Three depth limit reached"}
        return _build_action_response(game, round_obj, "flip_three", acting_player, outcome, target_player=target_player)

    discard_action_card_from_line(game, "flip_three", acting_player, target_player)

    drawn_cards = []
    deferred_actions = []

    for _ in range(3):
        drawn_card = draw_card_for_player(game, target_player)
        if not drawn_card:
            break

        definition = drawn_card.card_definition
        drawn_cards.append(
            {
                "card_name": definition.card_name,
                "effect_type": definition.effect_type,
                "effect_payload": definition.effect_payload,
                "value": definition.value,
            }
        )

        if definition.effect_payload == "second_chance":
            resolve_second_chance_draw(game, target_player, drawn_card)
        elif definition.effect_payload == "freeze":
            deferred_actions.append("freeze")
        elif definition.effect_payload == "flip_three":
            deferred_actions.append("flip_three")

        duplicate_result = _resolve_duplicate_with_second_chance(game, target_player, drawn_card)
        if duplicate_result["duplicate"] and not duplicate_result["saved_by_second_chance"]:
            game_player = GamePlayer.objects.get(game=game, player=target_player)
            game_player.is_active = False
            game_player.is_busted = True
            game_player.save(update_fields=["is_active", "is_busted"])

            if not get_active_players(game):
                summary = finalize_round(round_obj)
                outcome = {
                    "round_ended": True,
                    "target_player_id": target_player.id,
                    "drawn_cards": drawn_cards,
                    "bust": True,
                    "second_chance_used": False,
                    "round_summary": summary["round_summary"],
                }
                return _build_action_response(game, round_obj, "flip_three", acting_player, outcome, target_player=target_player)

            next_player = get_next_active_player(game, acting_player)
            bust_turn = None
            if next_player is not None:
                bust_turn = Turn.objects.create(
                    game=game,
                    round=round_obj,
                    turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1,
                    acting_player=next_player,
                    action_type="flip_three",
                )
            outcome = {
                "round_ended": False,
                "target_player_id": target_player.id,
                "drawn_cards": drawn_cards,
                "bust": True,
                "second_chance_used": False,
            }
            return _build_action_response(game, round_obj, "flip_three", acting_player, outcome, target_player=target_player, next_turn=bust_turn)

        score, unique_count = calculate_round_score(game, target_player)
        if unique_count >= 7:
            round_obj.winner_player = target_player
            round_obj.save(update_fields=["winner_player"])
            summary = finalize_round(round_obj)
            outcome = {
                "round_ended": True,
                "target_player_id": target_player.id,
                "drawn_cards": drawn_cards,
                "flip_seven": True,
                "score": score + 15,
                "round_summary": summary["round_summary"],
            }
            return _build_action_response(game, round_obj, "flip_three", acting_player, outcome, target_player=target_player)

    for deferred_action in deferred_actions:
        if deferred_action == "freeze":
            freeze_result = handle_freeze(round_obj, acting_player, target_player)
            freeze_result["drawn_cards"] = drawn_cards
            freeze_result["deferred_action"] = "freeze"
            return freeze_result

        if deferred_action == "flip_three":
            nested_result = handle_flip_three(round_obj, acting_player, target_player, depth=depth + 1)
            nested_result["drawn_cards"] = drawn_cards + nested_result.get("drawn_cards", [])
            nested_result["deferred_action"] = "flip_three"
            return nested_result

    next_player = get_next_active_player(game, acting_player)
    turn = None
    if next_player is not None:
        turn = Turn.objects.create(
            game=game,
            round=round_obj,
            turn_number=Turn.objects.filter(game=game, round=round_obj).count() + 1,
            acting_player=next_player,
            action_type="flip_three",
        )

    outcome = {
        "round_ended": False,
        "target_player_id": target_player.id,
        "drawn_cards": drawn_cards,
        "bust": False,
    }
    return _build_action_response(game, round_obj, "flip_three", acting_player, outcome, target_player=target_player, next_turn=turn)


def build_game_state(game):
    round_obj = game.rounds.order_by("-id").first()
    deck_remaining = CardLocation.objects.filter(game=game, zone_type="deck").count()
    active_player_count = GamePlayer.objects.filter(game=game, is_active=True).count()
    players = []
    for game_player in game.game_players.order_by("seat_number"):
        score, unique_count = calculate_round_score(game, game_player.player)
        players.append({
            "player_id": game_player.player_id,
            "username": game_player.player.username,
            "display_name": game_player.player.display_name or game_player.player.username,
            "active": game_player.is_active,
            "is_busted": game_player.is_busted,
            "score": score,
            "total_score": game_player.final_score or 0,
            "unique_numbers": unique_count,
            "cards": [
                {
                    "card_name": location.card_instance.card_definition.card_name,
                    "value": location.card_instance.card_definition.value,
                    "effect_type": location.card_instance.card_definition.effect_type,
                    "effect_payload": location.card_instance.card_definition.effect_payload,
                }
                for location in get_player_line(game, game_player.player)
            ],
        })
    turn = Turn.objects.filter(game=game, round=round_obj).order_by("-id").first() if round_obj else None
    return {
        "game_id": game.id,
        "game_code": game.game_code,
        "status": game.status,
        "target_score": game.target_score,
        "round_id": round_obj.id if round_obj else None,
        "round_ended": bool(round_obj and round_obj.ended_at),
        "active_player_count": active_player_count,
        "deck_remaining": deck_remaining,
        "current_turn": turn.acting_player_id if turn else None,
        "players": players,
    }
