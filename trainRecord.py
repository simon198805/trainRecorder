import datetime
import json
import csv

csvFileName = 'workouts.csv'
workoutOptionFileName = 'options.json'
timeFormatString = "%Y-%m-%d %H:%M:%S"

workoutNames = []
categories = {}
optionJsonData = {}

def readWorkoutOptions():
    with open(workoutOptionFileName) as f:
        global optionJsonData
        optionJsonData = json.loads(f.read())
        print(type(optionJsonData))
        f.close()
        for workoutRec in optionJsonData['workouts']:
            workoutNames.append(workoutRec['Name'])
            for category in workoutRec['categories']:
                if category not in categories.keys():
                    categories[category] = []
                categories[category].append(workoutRec['Name'])

def getLastWorkoutIdFromCsv()->int:
    with open(csvFileName, 'r') as csvFile:
        lstRec = list(csv.reader(csvFile))
        csvFile.close()
        if len(lstRec) > 0:
            lastRec = lstRec[-1]
            if lastRec[1] in workoutNames:
                return workoutNames.index(lastRec[1])
    return 0


def selectWorkoutByCategory():
    categoriesKeys = list(categories.keys())
    for keyId in range(len(categoriesKeys)):
        print(str(keyId) + ": " + categoriesKeys[keyId])

    while True:
        inVal = int(input('which category?'))
        if (inVal >= len(categoriesKeys) or inVal < 0):
            continue
        selectedCat = categories[categoriesKeys[inVal]]
        for id in range(len(selectedCat)):
            print(str(id) + ": " + selectedCat[id])
        inVal = int(input('which workout?'))
        if (inVal >= len(selectedCat) or inVal < 0):
            continue
        workout = selectedCat[inVal]
        workoutId = workoutNames.index(workout)
        break
    return workoutId, workout


def selectWorkoutNumeric(inVal):
    workoutId = int(inVal)
    if workoutId < 0 or workoutId >= len(workoutNames):
        raise ValueError("invalid id " + str(workoutId))
    workout = workoutNames[workoutId]
    return workoutId, workout


def addWorkout(inVal):
    if inVal in workoutNames:
        workout = inVal
        workoutId = workoutNames.index(workout)
    else:
        addConfirm = input('Add workout "' + inVal + '"?(N/y) ')
        if addConfirm.lower() == 'y':
            global optionJsonData
            optionJsonData['workouts'].append({'Name': inVal, 'categories': []})
            jObj = json.dumps(optionJsonData, indent=4)
            with open('options.json', 'w') as f:
                f.write(jObj)
            workoutNames.append(inVal)
            workout = inVal
            workoutId = workoutNames.index(workout)
        else:
            raise NameError("user canceled")
    return workoutId, workout


def getLastSameWorkoutFromCsv(workout):
    with open(csvFileName, 'r') as csvFile:
        for row in reversed(list(csv.reader(csvFile))):
            if (len(row)) < 4:
                # skip invalid row
                continue
            if row[1] == workout:
                lastTimeStamp = datetime.datetime.strptime(row[0], timeFormatString)
                lastSameWorkoutHrs = (datetime.datetime.now() - lastTimeStamp).total_seconds()/60/60
                print("It's " + str(int(lastSameWorkoutHrs)) + ' hrs from last "' + workout + '"')
                lastRep = row[3]
                lastWeight = row[2]
                return lastTimeStamp, lastRep, lastWeight


def getWeightAndRep(lastWeight, lastRep):
    weight = rep = ''

    inputs = input("weight(Kg)?(" + lastWeight + '), q to select new workout. ')
    # use last weight
    if inputs == '':
        inputs = lastWeight
    if inputs == 'q':
        raise NameError("user cancel")

    inputs = inputs.split()
    weight = inputs[0]

    if len(inputs) == 2:
        rep = inputs[1]

    if rep == '':
        rep = input("rep?(" + lastRep + ") ")
        if rep == '':
            rep = lastRep
        if rep == 'q':
            raise NameError("user cancel")
    return weight, rep


def printRecordAndWriteToCsv(timeStamp, workout, weight, rep, lastTimeStamp):
    duration = datetime.timedelta(seconds=((timeStamp - lastTimeStamp).seconds))

    workOutType = 'warm up' if int(rep) > 12 else 'training'
    List = [timeStamp.strftime(timeFormatString),  # 0
            workout,                               # 1
            weight,                                # 2
            rep,                                   # 3
            workOutType,                           # 4
            str(duration)]                         # 5

    # append record to workout.csv
    with open(csvFileName, 'a') as csvFile:
        csv.writer(csvFile).writerow(List)
        csvFile.close()

    print('>>>>>>"' + workout + '" ' + str(weight) + '(kg)x' + str(rep) + ', in ' + str(duration) + '@' + timeStamp.strftime(timeFormatString))


def main():
    readWorkoutOptions()

    # init last recorders
    lastWorkoutId = 0
    lastWeight = '0'
    lastRep = '20'
    lastTimeStamp = datetime.datetime.now()

    lastWorkoutId = getLastWorkoutIdFromCsv()

    print("work out start at:" + lastTimeStamp.strftime(timeFormatString))

    while True:
        # print workout options        
        for id in range(len(workoutNames)):
            print(str(id) + ": " + workoutNames[id])

        # add first workout

        inVal = input("which work out? q:exit, c: select by category, or enter the workout name to search or add (" + str(lastWorkoutId) + ": " + workoutNames[lastWorkoutId] + ') ')
        # use last workout
        if inVal == '':
            workoutId = lastWorkoutId
            workout = workoutNames[workoutId]
        # quit
        elif inVal == 'q':
            break
        # select by category 
        elif inVal == 'c':
            workoutId, workout = selectWorkoutByCategory()
        # select from list
        elif inVal.isnumeric():
            try:
                workoutId, workout = selectWorkoutNumeric(inVal)
            except Exception as e:
                print(e)
                continue
        else:
            try:
                workoutId, workout = addWorkout(inVal)
            except NameError as e:
                print(e)
                continue

        # get last same workout
        lastTimeStamp, lastRep, lastWeight = getLastSameWorkoutFromCsv(workout)

        # get weight and rep
        while True:
            try:
                weight, rep = getWeightAndRep(lastWeight, lastRep)
            except NameError as e:
                print(e)
                continue
            
            timeStamp = datetime.datetime.now()
            printRecordAndWriteToCsv(timeStamp, workout, weight, rep, lastTimeStamp)

            lastRep = rep
            lastWeight = weight
            lastWorkoutId = workoutId
            lastTimeStamp = timeStamp


if __name__ == '__main__':
    main()
