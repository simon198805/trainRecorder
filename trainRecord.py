import datetime
import json
from csv import writer

csvFileName = 'workouts.csv'

timeFormatString = "%Y-%m-%d %H:%M:%S"

with open('options.json') as f:
    data = json.load(f)
    f.close()

workoutNames = []
for workoutRec in data['workouts']:
    workoutNames.append(workoutRec['Name'])

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
                data['workouts'].append({'Name': inVal})
                with open('options.json', 'w') as f:
                    json.dump(data, f)
                    f.close()
                workoutNames.append(inVal)

            else:
                continue

        workout = inVal
        workoutId = workoutNames.index(inVal)
        
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

        workOutType = 'warm up' if int(rep) < 13 else 'training'
        List = [timeStamp.strftime(timeFormatString), workout, weight, rep, workOutType, str(duration) ]

        lastRep = rep
        lastWeight = weight
        lastWorkoutId = workoutId
        lastTimeStamp = timeStamp

        with open(csvFileName, 'a') as csvFile:
            csvWriter = writer(csvFile)
            csvWriter.writerow(List)
            csvFile.close()
        
        print('>>>>>>"' + workout + '" ' + str(weight) + '(kg)x' + str(rep) + ', in ' + str(duration) + '@' + timeStamp.strftime(timeFormatString))
