from django.db import models
from django.db.models import Q


class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Game(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('finished', 'Finished'),
        ('abandoned', 'Abandoned'),
    ]
    game_code = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_games')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    target_score = models.IntegerField(default=200)
    ruleset_version = models.CharField(max_length=50, default='v1')
    created_at = models.DateTimeField(auto_now_add=True)


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_memberships')
    seat_number = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_busted = models.BooleanField(default=False)
    final_score = models.IntegerField(null=True, blank=True)
    ranking = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'player'], name='uniq_game_player_membership'),
            models.UniqueConstraint(fields=['game', 'seat_number'], name='uniq_game_seat_number'),
            models.CheckConstraint(check=Q(seat_number__gt=0), name='gameplayer_seat_positive'),
        ]


class CardDefinition(models.Model):
    card_name = models.CharField(max_length=100)
    suit = models.CharField(max_length=20, blank=True)
    rank = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20, blank=True)
    value = models.IntegerField(null=True, blank=True)
    effect_type = models.CharField(max_length=50, blank=True)
    effect_payload = models.TextField(blank=True)
    is_special = models.BooleanField(default=False)


class Deck(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='decks')
    deck_name = models.CharField(max_length=100)
    deck_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class CardInstance(models.Model):
    card_definition = models.ForeignKey(CardDefinition, on_delete=models.CASCADE, related_name='instances')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='card_instances')
    deck = models.ForeignKey(Deck, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    created_at = models.DateTimeField(auto_now_add=True)


class CardLocation(models.Model):
    card_instance = models.ForeignKey(CardInstance, on_delete=models.CASCADE, related_name='locations')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='card_locations')
    zone_type = models.CharField(max_length=30)
    owner_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_cards')
    position_in_zone = models.IntegerField(null=True, blank=True)
    is_face_up = models.BooleanField(default=True)
    moved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(zone_type__in=['deck', 'line', 'discard']),
                name='cardlocation_valid_zone',
            ),
            models.CheckConstraint(
                check=(Q(zone_type='line') & Q(owner_player__isnull=False))
                | (Q(zone_type__in=['deck', 'discard']) & Q(owner_player__isnull=True)),
                name='cardlocation_owner_zone_consistency',
            ),
        ]


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_rounds')


class Turn(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='turns')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    acting_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='turns')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    action_type = models.CharField(max_length=50)
    result_summary = models.TextField(blank=True)


class TurnAction(models.Model):
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='actions')
    card_instance = models.ForeignKey(CardInstance, on_delete=models.SET_NULL, null=True, blank=True, related_name='turn_actions')
    target_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_actions')
    action_detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GameResult(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_results')
    score = models.IntegerField(default=0)
    ranking = models.IntegerField()
    is_winner = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'player'], name='uniq_result_game_player'),
        ]
