from datetime import datetime
from src.kickbase_trader import KickbaseLeagueUpdater


kickbaseUpdater = KickbaseLeagueUpdater()
kickbaseUpdater.collectGift()
kickbaseUpdater.getFeeds()
kickbaseUpdater.getTrades()

stats = kickbaseUpdater.getUserStats(kickbaseUpdater.user)
print(stats.team_value)
stats.teamValues[datetime.now()] = (stats.team_value)


for key, value in stats.teamValues.items():
    date = key
    team_value = value
    #print(date, value)

kickbaseUpdater.get_lineup()
kickbaseUpdater.getMarket()
kickbaseUpdater.getOwnMarketPlayersRising()
kickbaseUpdater.getOwnMarketPlayersFalling()
kickbaseUpdater.get_players_without_offer()
