# -*- coding: utf-8 -*-
import owlready2
import json
import operator
import requests
import time
from Annotation.EventData import *
'''
relayText
        "inn":1,
        "btop":1,                                                => away attack
        
        "seqno":2,
        "pitchId":"180508_182923",
        "batstartorder":1, "batorder":1,
        "ilsun":0,                                              => nth batting
        
        "ballcount":1,
        "s":0, "b":1, "o":0,
        "homeBallFour":0, "awayBallFour":0,  
        
        
        "base3":0, "base1":0, "base2":0,
        
        "homeInningScore":0, "awayInningScore":0,
        "homeScore":0, "awayScore":0,
        "homeHit":0, "awayHit":0,
        "homeError":0, "awayError":0,
        
        "stuff":"SLID"
        
        "liveText":"1구 볼",
        "textStyle":1,
------------------------------------------------------------------------------------------------------------------------
ballData
        "inn":1,
        "pitchId":"180508_182923",
        
        "ballcount":1,
    
        "pitcherName":"소사",
        "batterName":"전준우",
        
        "crossPlateX":-0.171643,
        "topSz":3.68897,
        "crossPlateY":1.4167,
        "vy0":-124.287,
        "vz0":-1.36267,
        "vx0":3.1259,
        "z0":5.95536,
        "y0":50.0,
        "ax":-0.553696,
        "x0":-1.40222,
        "ay":26.1504,
        "az":-22.3011,
        "bottomSz":1.66,
        "stance":"R",
        
        "stuff":"슬라이더",
        "speed":"136"
'''

class RuleData():

    def __init__(self, gameName):

        fileName = "_data/"+gameName+"/"+gameName + ".txt"
        data_file = open(fileName, "rt", encoding="UTF8")
        data = json.load(data_file)
        data_file.close()

        ball_fileName = "_data/" + gameName + "/" + gameName + "_ball.txt"
        ball_data_file = open(ball_fileName, "rt", encoding="UTF8")
        self.ball_data = json.load(ball_data_file)
        ball_data_file.close()

        self.set_game_info(data["gameInfo"])

        awayTeamPitchers, awayTeamBatters = self.set_TeamLineUp(data["awayTeamLineUp"])
        homeTeamPitchers, homeTeamBatters = self.set_TeamLineUp(data["homeTeamLineUp"])

        self.LineUp = {"AwayPitchers" : awayTeamPitchers, "AwayBatters" : awayTeamBatters, "HomePitchers" : homeTeamPitchers, "HomeBatters" : homeTeamBatters}

        self.relayTexts = self.set_relayTexts(data["relayTexts"])

    def set_game_info(self, game_info):
        '''"gameInfo"

        "aFullName":"롯데 자이언츠",
        "hPCode":"62698",
        "hCode":"LG",
        "hName":"LG",
        "cancelFlag":"N",
        "gdate":20180508,
        "aPCode":"68526",
        "round":4,
        "gtime":"18:30",
        "aName":"롯데",
        "gameFlag":"0",
        "hFullName":"LG 트윈스",
        "stadium":"잠실",
        "aCode":"LT",
        "optionFlag":1,
        "ptsFlag":"Y",
        "statusCode":"4"
        '''

        FhomeTeam = game_info["hFullName"]
        FawayTeam = game_info["aFullName"]

        homeTeam = game_info["hName"]
        awayTeam = game_info["aName"]



        homeCode = game_info["hCode"]
        awayCode = game_info["aCode"]

        date = game_info["gdate"]

        stadium = game_info["stadium"]

        self.GameInfo = {"homeTeam": homeTeam, "awayTeam": awayTeam, "stadium": stadium, "data" : date, "DateHomeAway" : str(date)+str(homeCode)+str(awayCode)}

        #input of ontology (game)

        return 1

    def set_TeamLineUp(self, TeamLineUp):
        pitchers = TeamLineUp["pitcher"]
        batters = TeamLineUp["batter"]

        batters.sort(key=operator.itemgetter("batOrder"))

        return pitchers, batters

    def set_relayTexts(self, relayTexts):
        newlist = []
        newlist = newlist + relayTexts['1']
        newlist = newlist + relayTexts['2']
        newlist = newlist + relayTexts['3']
        newlist = newlist + relayTexts['4']
        newlist = newlist + relayTexts['5']
        newlist = newlist + relayTexts['6']
        newlist = newlist + relayTexts['7']
        newlist = newlist + relayTexts['8']
        newlist = newlist + relayTexts['9']
        newlist = newlist + relayTexts['currentBatterTexts']
        newlist = newlist + [relayTexts['currentOffensiveTeam']]
        newlist = newlist + [relayTexts['currentBatter']]

        newlist.sort(key=operator.itemgetter("seqno"))

        return newlist

    def get_time_delta_between_two_pichId(self, A, B):
        A_h = A[:2]
        A_m = A[2:4]
        A_s = A[4:]

        B_h = B[:2]
        B_m = B[2:4]
        B_s = B[4:]

        return 3600 * (int(B_h) - int(A_h)) + 60 * (int(B_m) - int(A_m)) + (int(B_s) - int(A_s))

    def add_time_delta_between_two_pichId(self, A, B):
        A_h = A[:2]
        A_m = A[2:4]
        A_s = A[4:]

        B_h = B[:2]
        B_m = B[2:4]
        B_s = B[4:]

        return 3600 * (int(B_h) + int(A_h)) + 60 * (int(B_m) + int(A_m)) + (int(B_s) + int(A_s))

    def secondTotime(self, sec):
        h = format(sec // 3600, '02')
        m = format((sec % 3600) // 60, '02')
        s = format(sec % 60, '02')
        sec = h + m + s
        return sec

    def set_Start(self, count_delta, fps, o_start):
        start = int(count_delta / fps)
        start = self.secondTotime(start)
        start = self.add_time_delta_between_two_pichId(o_start, start)
        start = self.secondTotime(start)
        self.start_pitchId = start
        no = 0

        for i in self.relayTexts:
            if (int(i["pitchId"].split("_")[-1]) > int(start)):
                no = i["seqno"]
                break
            print(i["liveText"])

        self.relayTexts = self.relayTexts[no:]

    def find_ball_data_with_pitchId(self, pitchId):
        for i in self.ball_data:
            if(pitchId == i["pitchId"]):
                return i

        return None

    def get_Annotation(self):
        owlready2.onto_path.append("_data/_owl/")
        onto = owlready2.get_ontology("180515SKOB.owl")
        onto.load()

        PB = PitchingBatting(self.GameInfo, self.LineUp, onto)
        C = Change(self.GameInfo, self.LineUp, onto)
        R = Result(self.GameInfo, self.LineUp, onto)

        pre_pitchId = "000000_"+str(self.start_pitchId)
        print(pre_pitchId)
        #pre_pitchId = self.relayTexts[0]["pitchId"]

        for relayText in self.relayTexts:
            pitchId = relayText["pitchId"]
            ball_data = self.find_ball_data_with_pitchId(pitchId)

            if (ball_data is None):
                if(relayText["ballcount"] == 0): #모든 교체(수비위치, 타석, 주자, 팀공격)
                    C.set(relayText)
                else:
                    R.set(relayText)

            else:  # pitching and batting
                interval = self.get_time_delta_between_two_pichId(pre_pitchId.split("_")[-1], pitchId.split("_")[-1])
                #time.sleep(interval)

                PB.set(relayText, ball_data)
                pre_pitchId = pitchId

            #print(relayText["liveText"]+ "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

