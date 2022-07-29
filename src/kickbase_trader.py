from typing import Union
from kickbase_api.kickbase import Kickbase
from datetime import datetime, timezone

from kickbase_analysis.kickbase_analysis import KickbaseAnalysis
from kickbase_analysis.models.trade import Trade, TradePartner

from kickbase_api.models.base_model import BaseModel
from secrets import email as email, password as password


class PlayerStats(BaseModel):
    market_value_change: int = None
    market_value_change_percent: float = None

    def __init__(self, d: dict = {}):
        self._json_transform = {
        }
        self._json_mapping = {
            "marketValueChange": "market_value_change",
            "marketValueChangePercent": "market_value_change_percent"
        }
        super().__init__(d)


class KickbaseLeagueUpdater:
    kickbase = Kickbase()
    allPlayers = ""
    user = ""
    league = ""
    leagues = ""
    league_me = ""
    own_players = ""
    users = ""
    market = ""

    def __init__(self):
        self.user, self.leagues = self.kickbase.login(email, password)

        self.league = self.leagues[0]
        self.own_players = self.getLeagueUserPlayers(self.user.id)
        self.users = self.kickbase.league_users(self.league)
        self.league_me = self.kickbase.league_me(self.league)
        print(self.league_me.budget)
        print(self.league_me.placement)
        print(self.league_me.points)
        print(self.league_me.team_value)
        self.max_minus = (self.league_me.team_value + self.league_me.budget) * 0.33
        print(self.max_minus)
        print(self.league_me.proExpiry)
        return
    
    def getLeagueUserPlayers(self, user_id):
        return self.kickbase.league_user_players(self.league, user_id)


    def getLeagueUserPlayer(self, user_id, player_id):
        players = self.kickbase.league_user_players(self.league, user_id)
        for player in players:
            if player.id == player_id:
                return player
        return

    def getAllPlayers(self):
        if self.allPlayers == "":
            team_ids = [2,3,4,5,7,9,11,13,14,15,18,19,20,22,24,28,40,43]
            playerlist = []
            for x in team_ids:
                for player in self.kickbase.team_players(x):
                    playerlist.append(player)
            self.allPlayers = playerlist
        return self.allPlayers

    def collectGift(self):
        gift = self.kickbase.league_current_gift(self.league)
        is_available = gift.is_available
        amount = gift.amount
        level = gift.level
        gift_info = f"Geschenk: Verfügbar: {is_available}, Betrag: {amount}, Level: {level}"
        print(gift_info)
        try:
            collected = self.kickbase.league_collect_gift(self.league)
            print(collected)
        except Exception as e:
            print(e)

    def findPlayer(self, player_id):
        players = self.getAllPlayers()
        for player in players:
            if player.id == player_id:
                return player

    def getTrades(self):
        trades = KickbaseAnalysis.get_trades(self.feeds)
        for trade in trades:
            print("########VERKAUF########")
            print(f"Spieler: {trade.player_last_name}")
            player = ""
            if trade.buyer_type != TradePartner.KICKBASE:
                player = self.getLeagueUserPlayer( trade.buyer_id, trade.player_id)
            else:
                player = self.findPlayer(trade.player_id)
            print(f"Käufer: {trade.buyer_name} {trade.buyer_type}")
            print(f"Verkäufer: {trade.seller_name} {trade.seller_type}")
            try:
                market_value_difference = trade.price - player.marketValue
                market_value_difference_percent = (market_value_difference / player.marketValue) *100
                print(f"Marktwert: {player.marketValue} Preis: {trade.price} Differenz : {market_value_difference} Prozentualer Unterschied: {market_value_difference_percent}")
            except Exception as e:
                print(f"Spieler aus der Liga: {trade.price}")
                

            print("################")
    def getMarket(self):
        self.market = self.kickbase.market(self.league)

    def getOwnMarketPlayersRising(self):
        print("#########TRANSFERMARKT STEIGEND##########")
        playerlist = []
        for player in self.market.players:
            if player.marketValueTrend == 1 and player.user_id == self.user.id:
                print(f"{player.firstName} {player.lastName} {player.marketValue} ")
                if player.offers:
                    for offer in player.offers:
                        print(f"    Angebot: {offer.price} {offer.valid_until_date}")
                        offerOK = offer.price >= player.marketValue
                        print(f"        annehmbar: {offerOK}")
                playerlist.append(player)
        print("###################")
        self.own_rising_players = playerlist

    def getOwnMarketPlayersFalling(self):
        print("#########TRANSFERMARKT Fallend##########")
        playerlist = []
        for player in self.market.players:
            if player.marketValueTrend == 2 and player.user_id == self.user.id:
                print(f"{player.firstName} {player.lastName} {player.marketValue}")
                if player.offers:
                    for offer in player.offers:
                        print(f"    Angebot: {offer.price} {offer.valid_until_date}")
                        offerOK = offer.price >= player.marketValue
                        print(f"        annehmbar: {offerOK}")
                playerlist.append(player)
        print("###################")
        self.own_falling_players = playerlist

    def getFeeds(self):
        self.feeds = self.kickbase.league_feed(-10, self.league)
        self.feeds = KickbaseAnalysis.filter_feed_items_by_date(self.feeds, start_from=datetime(year=2020, month=8, day=16, hour=19, minute=0, tzinfo=timezone.utc))

    def getUserStats(self, user_id):
        return self.kickbase.league_user_stats(self.league, user_id)

    def league_user_player_stats(self,  player) -> PlayerStats:
        league_id = self.kickbase._get_league_id(self.league)
        player_id = self.kickbase._get_player_id(player)
        r = self.kickbase._do_get("/leagues/{}/players/{}/stats".format(league_id, player_id), True)
        print(r.json())
        if r.status_code == 200:
            return PlayerStats(r.json()["leaguePlayer"])
        else:
            raise Exception()

    def get_lineup(self):
        """ LINEUP """
        lineup = self.kickbase.line_up(self.league)
        goalie = ""
        defenders = ""
        midfielders = ""
        attackers = ""
        for player_num in lineup.players:
            player = self.getLeagueUserPlayer( self.user, player_num)
            position = player.position
            if position == 1:
                goalie += (f" - {player.first_name} {player.last_name}")
            if position == 2:
                defenders += (f" - {player.first_name} {player.last_name}")
            if position == 3:
                midfielders += (f" - {player.first_name} {player.last_name}")
            if position == 4:
                attackers += (f" - {player.first_name} {player.last_name}")
        print(lineup.type)
        print(goalie)
        print(defenders)
        print(midfielders)
        print(attackers)

    def get_players_without_offer(self):
        print("Bisher ohne Angebote: ")
        for player in self.market.players:
            if player.offers:
                for offer in player.offers:
                    continue
            else:
                #Das funktioniert tatsächlich => so können Schnäppchen gefunden werden
                #marketValueTrend 1 => steigend, 2 => fallend
                trend = " - fallend"
                if player.marketValueTrend == 1:
                    trend = " + steigend"
                    #playerStats = self.league_user_player_stats(player)
                    #print(dir(playerStats))
                print(f"{player.first_name} {player.last_name}      {player.marketValue}    {player.expiry}     {trend}")
