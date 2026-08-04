from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, GameViewSet, GamePlayerViewSet, CardDefinitionViewSet, DeckViewSet, CardInstanceViewSet, CardLocationViewSet, RoundViewSet, TurnViewSet, TurnActionViewSet

router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'game-players', GamePlayerViewSet)
router.register(r'card-definitions', CardDefinitionViewSet)
router.register(r'decks', DeckViewSet)
router.register(r'card-instances', CardInstanceViewSet)
router.register(r'card-locations', CardLocationViewSet)
router.register(r'rounds', RoundViewSet)
router.register(r'turns', TurnViewSet)
router.register(r'turn-actions', TurnActionViewSet)

urlpatterns = [
    path('games/create/', GameViewSet.as_view({'post': 'create'}), name='game-create'),
    path('games/<int:pk>/results/', GameViewSet.as_view({'get': 'results'}), name='game-results'),
    path('games/<int:pk>/rules/validate/', GameViewSet.as_view({'post': 'rules_validate'}), name='game-rules-validate'),
    path('games/<int:pk>/rules/resolve/', GameViewSet.as_view({'post': 'rules_resolve'}), name='game-rules-resolve'),
    path('games/<int:game_pk>/rounds/<int:pk>/score/calculate/', RoundViewSet.as_view({'post': 'score_calculate'}), name='round-score-calculate'),
    path('games/<int:game_pk>/rounds/<int:pk>/score/apply/', RoundViewSet.as_view({'post': 'score_apply'}), name='round-score-apply'),
    path('games/<int:game_pk>/rounds/<int:pk>/actions/bust/', RoundViewSet.as_view({'post': 'bust'}), name='round-action-bust'),
    path('games/<int:game_pk>/rounds/<int:pk>/actions/flip-seven/', RoundViewSet.as_view({'post': 'flip_seven'}), name='round-action-flip-seven'),
    path('games/<int:game_pk>/rounds/<int:pk>/end-check/', RoundViewSet.as_view({'post': 'end_check'}), name='round-end-check'),
    path('', include(router.urls)),
]
