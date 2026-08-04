from rest_framework import serializers
from .models import Player, Game, GamePlayer, CardDefinition, Deck, CardInstance, CardLocation, Round, Turn, TurnAction


class PlayerSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        username = (value or '').strip()
        if len(username) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters long.')
        return username

    class Meta:
        model = Player
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class GamePlayerSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        game = attrs.get('game') or getattr(self.instance, 'game', None)
        seat_number = attrs.get('seat_number', getattr(self.instance, 'seat_number', None))
        player = attrs.get('player') or getattr(self.instance, 'player', None)

        if seat_number is None or seat_number < 1:
            raise serializers.ValidationError({'seat_number': 'Seat number must be greater than 0.'})

        if game and seat_number is not None:
            seat_qs = GamePlayer.objects.filter(game=game, seat_number=seat_number)
            if self.instance:
                seat_qs = seat_qs.exclude(id=self.instance.id)
            if seat_qs.exists():
                raise serializers.ValidationError({'seat_number': 'Seat number is already taken in this game.'})

        if game and player:
            membership_qs = GamePlayer.objects.filter(game=game, player=player)
            if self.instance:
                membership_qs = membership_qs.exclude(id=self.instance.id)
            if membership_qs.exists():
                raise serializers.ValidationError({'player': 'Player is already part of this game.'})

        return attrs

    class Meta:
        model = GamePlayer
        fields = '__all__'


class CardDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDefinition
        fields = '__all__'


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = '__all__'


class CardInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardInstance
        fields = '__all__'


class CardLocationSerializer(serializers.ModelSerializer):
    VALID_ZONES = {'deck', 'line', 'discard'}

    def validate_zone_type(self, value):
        if value not in self.VALID_ZONES:
            raise serializers.ValidationError('zone_type must be one of deck, line, discard.')
        return value

    def validate(self, attrs):
        zone_type = attrs.get('zone_type', getattr(self.instance, 'zone_type', None))
        owner_player = attrs.get('owner_player', getattr(self.instance, 'owner_player', None))

        if zone_type == 'line' and owner_player is None:
            raise serializers.ValidationError({'owner_player': 'owner_player is required for line zone.'})

        if zone_type in {'deck', 'discard'} and owner_player is not None:
            raise serializers.ValidationError({'owner_player': 'owner_player must be null for deck/discard zones.'})

        return attrs

    class Meta:
        model = CardLocation
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    def validate_round_number(self, value):
        if value < 1:
            raise serializers.ValidationError('round_number must be greater than 0.')
        return value

    class Meta:
        model = Round
        fields = '__all__'


class TurnSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        game = attrs.get('game') or getattr(self.instance, 'game', None)
        acting_player = attrs.get('acting_player') or getattr(self.instance, 'acting_player', None)
        turn_number = attrs.get('turn_number', getattr(self.instance, 'turn_number', None))

        if turn_number is None or turn_number < 1:
            raise serializers.ValidationError({'turn_number': 'turn_number must be greater than 0.'})

        if game and acting_player and not GamePlayer.objects.filter(game=game, player=acting_player).exists():
            raise serializers.ValidationError({'acting_player': 'acting_player must be a member of this game.'})

        return attrs

    class Meta:
        model = Turn
        fields = '__all__'


class TurnActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurnAction
        fields = '__all__'
