import datetime
import json
import csv

csvFileName = 'workouts.csv'

timeFormatString = "%Y-%m-%d %H:%M:%S"

with open('options.json') as f:
    data = json.load(f)
    f.close()

workoutNames = []
categories = {}
for workoutRec in data['workouts']:
    workoutNames.append(workoutRec['Name'])
    for category in workoutRec['categories']:
        if category not in categories.keys():
            categories[category] = []
        categories[category].append(workoutRec['Name'])

print(categories)

lastWorkoutId = 0
lastWeight = '0'
lastRep = '20'
lastTimeStamp = datetime.datetime.now()

print("work out start at:" + lastTimeStamp.strftime(timeFormatString))

while True:
    # print workout options        
    id = 0
    for workoutName in workoutNames:
        print(str(id) + ": " + workoutName)
        id = id + 1

    inVal = input("which work out? (" + str(lastWorkoutId) + ": " + workoutNames[lastWorkoutId] + ') ')
    if inVal == '':
        workoutId = lastWorkoutId
        workout = workoutNames[workoutId]
    elif inVal == 'q':
        break
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

    while True:
        weight = rep = ''

        inputs = input("weight(Kg)?(" + lastWeight + '), q to select new workout. ')
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

        with open(csvFileName, 'a') as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(List)
            csvFile.close()
        
        print('>>>>>>"' + workout + '" ' + str(weight) + '(kg)x' + str(rep) + ', in ' + str(duration) + '@' + timeStamp.strftime(timeFormatString))
