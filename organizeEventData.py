import json
import datetime
from dateutil.relativedelta import relativedelta
import math

def teamNameFromId(id, teams):
    for team in teams:
        if(team["wyId"]==id):
            return team["name"]

def calcAveragePassLength(passes):
    totalPassDistance = 0
    for p in passes:
        passPositions = p["positions"]
        curPassLength = math.sqrt((passPositions[1]["x"] - passPositions[0]["x"])**2 + (passPositions[1]["y"] - passPositions[0]["y"])**2)
        totalPassDistance += curPassLength
    if(len(passes) == 0):
        return 0
    return totalPassDistance/len(passes)


def calcPercentageOfFinalThirdPasses(passes):
    totalPasses =0
    passesFirstThird = 0
    passesSecondThird = 0
    passesFinalThird = 0
    for p in passes:
        totalPasses+=1
        passPositions = p["positions"]
        if(passPositions[1]["x"]<=33):
            passesFirstThird +=1
        elif(passPositions[1]["x"]>33 and passPositions[1]["x"]<=66):
            passesSecondThird +=1
        else:
            passesFinalThird +=1
    if(totalPasses!=0):
        return [passesFirstThird/totalPasses,passesSecondThird/totalPasses,passesFinalThird/totalPasses]
    else:
        return [0,0,0]

def getTeamIdsFromMatchId(id, matches, teams):
    for match in matches:
        if(match["wyId"]==id):
            teamIds = list(match["teamsData"].keys())
            return teamIds

# def getStartingLineupAverageHeight(match, playerMap):
#     team1 = True
#     team1Height = 0
#     team2Height = 0
#     for team in match["teamsData"]:
#         for player in match["teamsData"][team]["formation"]["lineup"]:
#             playerId = player["playerId"]
#             if(team1==True):
#                 team1Height+= playerMap[playerId]["height"]
#             else:
#                 team2Height+= playerMap[playerId]["height"]
#         team1 = False
#     return [team1Height/11, team2Height/11]

def getStartingLineupAverageHeight(match, playerMap):

    teamIds = list(match["teamsData"].keys())
    for t_id in teamIds:
        if match["teamsData"][t_id]['side'] == 'home':
            team1_id = t_id
        else:
            team2_id = t_id

    team1Height = 0
    team2Height = 0
    for team in teamIds:
        for player in match["teamsData"][team]["formation"]["lineup"]:
            playerId = player["playerId"]
            if (team == team1_id):
                team1Height+= playerMap[playerId]["height"]
            elif (team == team2_id):
                team2Height+= playerMap[playerId]["height"]

    return [team1_id, team1Height/11, team2_id, team2Height/11]


# def getStartingLineupAverageAge(match, playerMap):
#     team1Age = 0
#     team2Age = 0
#     team1 = True
#     matchDate = " ".join(match["date"].split()[:3])
#     matchDate = datetime.datetime.strptime(matchDate, '%B %d, %Y')
#     for team in match["teamsData"]:
#         for player in match["teamsData"][team]["formation"]["lineup"]:
#             playerId = player["playerId"]
#             playerBday = playerMap[playerId]["birthDate"]
#             playerBday = datetime.datetime.strptime(playerBday,"%Y-%m-%d")
#             age = relativedelta(matchDate, playerBday).years
#             if(team1==True):
#                 team1Age+= age
#             else:
#                 team2Age+= age
#         team1 = False
#     return [team1Age/11, team2Age/11]

def getStartingLineupAverageAge(match, playerMap):
    team1Age = 0
    team2Age = 0
    
    teamIds = list(match["teamsData"].keys())
    for t_id in teamIds:
        if match["teamsData"][t_id]['side'] == 'home':
            team1_id = t_id
        else:
            team2_id = t_id

    matchDate = " ".join(match["date"].split()[:3])
    matchDate = datetime.datetime.strptime(matchDate, '%B %d, %Y')

    for team in teamIds:
        for player in match["teamsData"][team]["formation"]["lineup"]:
            playerId = player["playerId"]
            playerBday = playerMap[playerId]["birthDate"]
            playerBday = datetime.datetime.strptime(playerBday,"%Y-%m-%d")
            age = relativedelta(matchDate, playerBday).years
            if (team == team1_id):
                team1Age+= age
            elif (team == team2_id):
                team2Age+= age

    return [team1_id, team1Age/11, team2_id, team2Age/11]

def createNewDictionary(intervals):
    eventsPer5 = {}
    for interval in intervals:
        eventsPer5[interval] = []
    return eventsPer5

#output a dictionary whose keys are the matchIds and values are also dictionaries that holds the events for each 5 minute bin
def groupEventsByMatch(events):
    intervals = ["5","10","15","20","25","30","35","40","45","45+","50","55","60","65","70","75","80","85", "90","90+"]
    prevMatchId = -1
    i = 0
    l = len(events)
    eventsPerMatch = {}
    numMatches =0
    while(i<l):
        intervalIndex = 0
        prevMatchId = events[i]["matchId"]
        #dictionary that holds an array of all events, in 5 minute bins
        eventsPer5 = createNewDictionary(intervals)
        firstHalf = True
        numMatches+=1
        #while the current event is from the same match as the previous one
        while(i < l and events[i]["matchId"]==prevMatchId):
            if(events[i]['matchPeriod']=='2H'):
                #incrementing from interval "45+" to "50"
                if(firstHalf==True):
                    intervalIndex+=1
                    firstHalf=False
                #if event occured in 2nd half, add the number of seconds in 1st half to it
                events[i]["eventSec"] += (45*60)
            curInterval = intervals[intervalIndex]
            if(curInterval!="45+" and curInterval!= "90+"):
                #if this events time exceeds the current bin, move to the next one
                if(events[i]["eventSec"]/60 > int(curInterval)):
                    intervalIndex+=1
                    curInterval = intervals[intervalIndex]
                        #adding event to the bin
            eventsPer5[curInterval].append(events[i])
            i+=1
        eventsPerMatch[prevMatchId] = eventsPer5
        if(numMatches%10==0):
            print("Done " + str(numMatches) + " matches")
    return eventsPerMatch

#Input: dictionary where keys are bin labels, and value is array of all events that occured in that bin
#Output: dictionary where keys are event type (ie: shot), and value is another dictionary of all events of that type split up into bins
def splitEventsByType(events, teamIds):
    intervals = ["5","10","15","20","25","30","35","40","45","45+","50","55","60","65","70","75","80","85", "90","90+"]
    team1Events = {"shot": createNewDictionary(intervals), "corner":createNewDictionary(intervals), "freeKickShots":createNewDictionary(intervals), "redCard":createNewDictionary(intervals),
        "yellowCard":createNewDictionary(intervals),
        "passes":createNewDictionary(intervals)}
    team2Events = {"shot": createNewDictionary(intervals), "corner":createNewDictionary(intervals), "freeKickShots":createNewDictionary(intervals), "redCard":createNewDictionary(intervals),
        "yellowCard":createNewDictionary(intervals),
        "passes":createNewDictionary(intervals)}
    for bin in events:
        for event in events[bin]:
            eventType = ""
            #includes corners and "corner like" free kicks
            if(event['subEventId'] == 30 or event['subEventId'] == 32):
                eventType = "corner"
            elif(event['subEventId'] == 33):
                eventType = "freeKickShots"
            elif(event['eventId']==10):
                eventType="shot"
            elif(event["eventName"] =='Foul'):
                #checking if foul resulted in red card or yellow card
                for tag in event["tags"]:
                    if(tag["id"]==1703 or tag["id"]==1701):
                        eventType = "redCard"
                        break
                    elif(tag["id"]==1702):
                        eventType = "yellowCard"
            elif(event['eventId']==8):
                eventType="passes"
            if(eventType!=""):
                if(event["teamId"]==int(teamIds[0])):
                    team1Events[eventType][bin].append(event)
                else:
                    team2Events[eventType][bin].append(event)
    return [team1Events, team2Events]

#calculates the number of event type for a match (ie: number of corners), and return a dictionary holding these values
def calcNumByEventType(eventsByType):
    numDict = {}
    for eventType in eventsByType:
        #when we are going through all a teams passes, we are going to calculate the percentage of passes that are passes INTO the final third
        if(eventType=="passes"):
            numDict["percentPassFirstThird"] = {}
            numDict["percentPassSecondThird"] = {}
            numDict["percentPassFinalThird"] = {}
            numDict["averagePassLength"] = {}
            for bin in eventsByType[eventType]:
                passes =eventsByType[eventType][bin]
                percentageByThird = calcPercentageOfFinalThirdPasses(passes)
                numDict["percentPassFirstThird"][bin] = percentageByThird[0]
                numDict["percentPassSecondThird"][bin] = percentageByThird[1]
                numDict["percentPassFinalThird"][bin] =percentageByThird[2]
                numDict["averagePassLength"][bin] = calcAveragePassLength(passes)
    #for all other event types, simply calculate the number of those events by the len function
        else:
            numDict[eventType] = {}
            for bin in eventsByType[eventType]:
                numDict[eventType][bin] = len(eventsByType[eventType][bin])
    return numDict

# matchesFile = open("data/matches/matches_england.json")
# matches = json.load(matchesFile)
# matchesMap = {}
# for match in matches:
#     matchesMap[match["wyId"]] = match
#     print("----------------------")
# matchesFile.close()

# teamsFile = open("data/teams.json")
# teams = json.load(teamsFile)
# teamsFile.close()

# playersFile = open("data/players.json")
# players = json.load(playersFile)
# playerMap = {}
# for player in players:
#     playerMap[player["wyId"]] =player
# playersFile.close()

# eventsFile = open("data/events/events_England.json")
# events = json.load(eventsFile)
# eventsFile.close()

#going through each match, splitting up the events by event type and then calculating the number of each event in that match
# eventsPerMatch = groupEventsByMatch(events)
# for match in eventsPerMatch:
#     teamIds =getTeamIdsFromMatchId(match,matches,teams)
#     team1Name =teamNameFromId(int(teamIds[0]), teams)
#     team2Name =teamNameFromId(int(teamIds[1]), teams)
#     #print(team1Name + " vs " + team2Name)
#     averageAge = getStartingLineupAverageAge(matchesMap[match], playerMap)
#     print(team1Name + ": " + str(averageAge[0]))
#     print(team2Name + ": " + str(averageAge[1]))
#     eventsPerMatch[match] = splitEventsByType(eventsPerMatch[match], teamIds)
#     team1Events = eventsPerMatch[match][teamIds[0]]
#     team2Events = eventsPerMatch[match][teamIds[1]]
#     team1NumDict = calcNumByEventType(team1Events)
#     team2NumDict = calcNumByEventType(team2Events)
#     print(team1Name + ": " + str(team1NumDict["averagePassLength"]))
#     print(team2Name + ": " + str(team2NumDict["averagePassLength"]))







