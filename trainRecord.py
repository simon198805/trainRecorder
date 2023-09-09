import datetime
import json
import csv

csvFileName = 'workouts.csv'

timeFormatString = "%Y-%m-%d %H:%M:%S"

# get workout names and categories from options.json
workoutNames = []
categories = {}
with open('options.json') as f:
    data = json.load(f)
    f.close()
    for workoutRec in data['workouts']:
        workoutNames.append(workoutRec['Name'])
        for category in workoutRec['categories']:
            if category not in categories.keys():
                categories[category] = []
            categories[category].append(workoutRec['Name'])

# init last recorders
lastWorkoutId = 0
lastWeight = '0'
lastRep = '20'
lastTimeStamp = datetime.datetime.now()

# get last workout for default select
with open(csvFileName, 'r') as csvFile:
    lstRec = list(csv.reader(csvFile))
    if len(lstRec) > 0:
        lastRec = lstRec[-1]
        if lastRec[1] in workoutNames:
            lastWorkoutId = workoutNames.index(lastRec[1])

print("work out start at:" + lastTimeStamp.strftime(timeFormatString))

while True:
    # print workout options        
    for id in range(len(workoutNames)):
        print(str(id) + ": " + workoutNames[id])

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
    # select from list
    elif inVal.isnumeric():
        workoutId = int(inVal)
        workout = workoutNames[workoutId]
    else:
        if inVal not in workoutNames:
            addConfirm = input('Add workout "' + inVal + '"?(N/y) ')
            if addConfirm.lower() == 'y':
                data['workouts'].append({'Name': inVal, 'categories': []})
                with open('options.json', 'w') as f:
                    json.dump(data, f)
                    f.close()
                workoutNames.append(inVal)

            else:
                continue

        workout = inVal
        workoutId = workoutNames.index(inVal)

    # get last same workout
    with open(csvFileName, 'r') as csvFile:
        for row in reversed(list(csv.reader(csvFile))):
            if (len(row)) < 4:
                continue
            if row[1] == workout:
                lastTimeStamp = datetime.datetime.strptime(row[0], timeFormatString)
                lastSameWorkoutHrs = (datetime.datetime.now() - lastTimeStamp).total_seconds()/60/60
                print("It's " + str(int(lastSameWorkoutHrs)) + ' hrs from last "' + workout + '"')
                lastRep = row[3]
                lastWeight = row[2]
                break

    # get weight and rep
    while True:
        weight = rep = ''

        inputs = input("weight(Kg)?(" + lastWeight + '), q to select new workout. ')
        # use last weight
        if inputs == '':
            inputs = lastWeight
        if inputs == 'q':
            break

        inputs = inputs.split()       
        weight = inputs[0]

        if len(inputs) == 2:
            rep = inputs[1]

        if rep == '':
            rep = input("rep?(" + lastRep + ") ")
            if rep == '':
                rep = lastRep
            if rep == 'q':
                break

        timeStamp = datetime.datetime.now()

        duration = datetime.timedelta(seconds=((timeStamp - lastTimeStamp).seconds))

        workOutType = 'warm up' if int(rep) > 12 else 'training'
        List = [timeStamp.strftime(timeFormatString),   # 0
                 workout,                               # 1
                 weight,                                # 2
                 rep,                                   # 3
                 workOutType,                           # 4
                 str(duration) ]                        # 5

        lastRep = rep
        lastWeight = weight
        lastWorkoutId = workoutId
        lastTimeStamp = timeStamp

        # append record to workout.csv
        with open(csvFileName, 'a') as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(List)
            csvFile.close()
        
        print('>>>>>>"' + workout + '" ' + str(weight) + '(kg)x' + str(rep) + ', in ' + str(duration) + '@' + timeStamp.strftime(timeFormatString))
