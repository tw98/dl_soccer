import json

def teamNameFromId(id, teams):
    for team in teams:
        if(team["wyId"]==id):
            return team["name"]

def getTeamIdsFromMatchId(id, matches, teams):
    for match in matches:
        if(match["wyId"]==id):
            teamIds = list(match["teamsData"].keys())
            return teamIds

def createNewDictionary(intervals):
    eventsPer5 = {}
    for interval in intervals:
        eventsPer5[interval] = []
    return eventsPer5

#output a dictionary whose keys are the matchIds and values are also dictionaries that holds the events for each 5 minute bin
def groupEventsByMatch(eventsFileName):
    eventsFile = open(eventsFileName)
    events = json.load(eventsFile)
    eventsFile.close()
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
def splitEventsByType(events):
    numCorners=0
    intervals = ["5","10","15","20","25","30","35","40","45","45+","50","55","60","65","70","75","80","85", "90","90+"]
    eventsByType = {"shot": createNewDictionary(intervals), "corner":createNewDictionary(intervals), "freeKickShots":createNewDictionary(intervals), "redCard":createNewDictionary(intervals),
        "yellowCard":createNewDictionary(intervals),
        "offside":createNewDictionary(intervals)}
    for bin in events:
        for event in events[bin]:
            eventType = ""
            #includes corners and corner like free kicks
            if(event['subEventId'] == 30 or event['subEventId'] == 32):
                numCorners+=1
                eventType = "corner"
            elif(event['subEventId'] == 33):
                eventType = "freeKickShots"
            elif(event['eventId']==10):
                eventType="shot"
            elif(event['eventId']==6):
                eventType="offside"
            elif(event["eventName"] =='Foul'):
                for tag in event["tags"]:
                    if(tag["id"]==1703 or tag["id"]==1701):
                        eventType = "redCard"
                        break
                    elif(tag["id"]==1702):
                        eventType = "yellowCard"
            if(eventType!=""):
                eventsByType[eventType][bin].append(event)
    return eventsByType

#calculates the number of event type for a match (ie: number of corners), and return a dictionary holding these values
def calcNumByEventType(events,teams):
    numDictTeam1 = {}
    numDictTeam2 = {}
    for key in events:
        s1=0
        s2=0
        for bin in events[key]:
            for event in events[key][bin]:
                if(event["teamId"]==int(teams[0])):
                    s1+=1
                else:
                    s2+=1
        numDictTeam1[key]=s1
        numDictTeam2[key]=s2
    return [numDictTeam1,numDictTeam2]

matchesFile = open("../matches/matches_England.json")
matches = json.load(matchesFile)
matchesFile.close()

teamsFile = open("../teams.json")
teams = json.load(teamsFile)
teamsFile.close()



eventsPerMatch = groupEventsByMatch("../events/events_England.json")
#going through each match, splitting up the events by event type and then calculating the number of each event in that match
for match in eventsPerMatch:
    teamIds =getTeamIdsFromMatchId(match,matches,teams)
    team1Name =teamNameFromId(int(teamIds[0]), teams)
    team2Name =teamNameFromId(int(teamIds[1]), teams)
    print(team1Name + " vs " + team2Name)
    eventsPerMatch[match] = splitEventsByType(eventsPerMatch[match])
    numDicts = calcNumByEventType(eventsPerMatch[match],teamIds)
    print(team1Name)
    for type in numDicts[0]:
        print("Number of " + type + ": " + str(numDicts[0][type]))
    print(team2Name)
    for type in numDicts[1]:
        print("Number of " + type + ": " + str(numDicts[1][type]))
    print("---------------")







