import datetime
import json
import csv


class UserCancelException(Exception):
    "User cancel"
    pass

csvFileName = 'workouts.csv'
workoutOptionFileName = 'options.json'
timeFormatString = "%Y-%m-%d %H:%M:%S"

workoutNames = []
categories = {}
optionJsonData = {'workouts': []}
workoutSelector = 'category'
lastSelectCat = ''


def getDatetimeFromStr(inVal: str) -> datetime.datetime:
    return datetime.datetime.strptime(inVal, timeFormatString)


def readWorkoutOptions():
    with open(workoutOptionFileName) as f:
        global optionJsonData
        try:
            optionJsonData = json.loads(f.read())
        except Exception as e:
            print(e)
            return
        f.close()
        for workoutRec in optionJsonData['workouts']:
            workoutNames.append(workoutRec['Name'])
            for category in workoutRec['categories']:
                if category not in categories.keys():
                    categories[category] = []
                categories[category].append(workoutRec['Name'])


def getClosestWorkoutDateInCsv(workout) -> datetime.datetime:
    with open(csvFileName, 'r') as csvFile:
        lstRec = list(csv.reader(csvFile))
        csvFile.close()
        for rec in reversed(lstRec):
            if len(rec) > 1:
                if rec[1] == workout:
                    return getDatetimeFromStr(rec[0])
        raise ValueError('workout "' + workout + '" not found')


def getLastWorkoutFromCsv():
    with open(csvFileName, 'r') as csvFile:
        lstRec = list(csv.reader(csvFile))
        csvFile.close()
        if len(lstRec) > 0:
            lastRec = lstRec[-1]
            if lastRec[1] in workoutNames:
                return lastRec[1]
    return ''


def printListWithId(targetList: list):
    for id in range(len(targetList)):
        print(str(id) + ": " + targetList[id])


def selectFromList(targetList: list, msg: str, defaultSelection: str = '', printList = True):
    """print and select an item from list, if user input a str matched item in the list, that item id will be return

    Args:
        targetList (list): the list to select from
        msg (str): message to show when user is asked for input

    Raises:
        ValueError: input an number but value is out of range

    Returns:
        int: select index
        str: user input str
    """
    if printList:
        printListWithId(targetList)
    while True:
        try:
            defaultId = -1
            if defaultSelection in targetList:
                defaultId = targetList.index(defaultSelection)
            defaultStr = (' (' + str(defaultId) + ': ' + defaultSelection + ')') if defaultId != -1 else ''
            inVal = input(msg + defaultStr)
            if inVal.isnumeric():
                if int(inVal) in range(len(targetList)):
                    return int(inVal)
                else:
                    raise ValueError('out of range')
            elif inVal in targetList:
                return targetList.index(inVal)
            elif inVal == '' and defaultId != -1:
                return defaultId
            else:
                return inVal
        except Exception as e:
            print(e)


def multiSelectOrAddCategories():
    while True:
        try:
            selectedCategories = []
            catKeys = categories.keys()
            inVal = input('select categories(multi select)')
            lstIn = inVal.split()
            for val in lstIn:
                if val.isnumeric():
                    selectedCategories.append(catKeys[int(val)])
                else:
                    selectedCategories.append(val)
                    if val not in catKeys:
                        categories[val] = []
            return selectedCategories
        except Exception as e:
            print(e)


def multiSelectFromList(targetList: list, msg: str):
    printListWithId(targetList)
    while True:
        try:
            inVal = input(msg + '(multi select)')
            lstIn = int(inVal.split())
            return targetList[lstIn]
        except Exception as e:
            print(e)


def askAddCategories():
    catName = input('category name?')
    if catName == 'q':
        return
    else:
        addCategory(catName)


def addCategory(catName:str):
    """add category to categories

    Args:
        catName (str): category name
    """
    if catName in categories:
        print(catName, ' existed')
    else:
        categories[catName] = []


def processSelectorChange(inVal):
    """check in input value is process control string

    Args:
        inVal (_type_): input valus

    Raises:
        UserCancelException: user cancel the process by select special options in input
    """
    global workoutSelector

    if not isinstance(inVal, str):
        return
    lowerVal = inVal.lower()
    if lowerVal == 'q':
        workoutSelector = 'selector'
        raise UserCancelException
    elif lowerVal == 'c':
        workoutSelector = 'category'
        raise UserCancelException
    elif lowerVal == 'f':
        workoutSelector = 'fullList'
        raise UserCancelException
    return


def printCategoriesWithLastWorkoutDelta():
    id = 0
    for cat,catWorkouts in categories.items():
        catDatetime = datetime.datetime.now()
        for workout in catWorkouts:
            try:
                lastWorkoutDate = getClosestWorkoutDateInCsv(workout)
            except Exception as e:
                #print(e)
                continue
            if catDatetime > lastWorkoutDate:
                catDatetime = lastWorkoutDate
        catDurationsHrs = (datetime.datetime.now() - catDatetime).total_seconds()/60/60
        print(id, ': ', cat, '(', int(catDurationsHrs), ')')
        id += 1


def selectCategory() -> str:
    """select category. if input category name, will ask if add category

    Returns:
        int: Selected category id
    """
    global lastSelectCat
    while True:
        try:
            printCategoriesWithLastWorkoutDelta()
            catKeys = list(categories.keys())
            inVal = selectFromList(catKeys, 'which category?', lastSelectCat, printList=False)
            processSelectorChange(inVal)
            if isinstance(inVal, int):
                lastSelectCat = catKeys[int(inVal)]
                return lastSelectCat
            else:
                if (input('Category ' + inVal + 'does not exist, add it?(N/y)') == 'y'):
                    addCategory(inVal)
                    lastSelectCat = inVal
                    return inVal
        except UserCancelException as e: raise
        except Exception as e:
            print(e)


def selectWorkoutByCategory():
    global workoutSelector
    cat = selectCategory()
    selectedCatWorkouts = categories[cat]
    while True:
        inVal = selectFromList(selectedCatWorkouts, 'which workout?')
        processSelectorChange(inVal)
        if type(inVal) == int:
            workout = selectedCatWorkouts[inVal]
            workoutId = workoutNames.index(workout)
            return workoutId, workout
        else:
            return addWorkout(inVal)


def selectSelector():
    global workoutSelector
    lstSelectors = ['category', 'fullList', 'add']
    try:
        workoutSelector = lstSelectors[selectFromList(lstSelectors, 'Select workout selector:')]
    except Exception as e:
        pass


def selectWorkout(lastWorkout):
    while True:
        if workoutSelector == 'category':
            return selectWorkoutByCategory()
        elif workoutSelector == 'fullList':
            return selectWorkoutInFullList(lastWorkout)
        elif workoutSelector == 'add':
            return askAddWorkout()
        else:
            selectSelector()
    

def selectWorkoutNumeric(inVal):
    workoutId = int(inVal)
    if workoutId < 0 or workoutId >= len(workoutNames):
        raise ValueError("invalid id " + str(workoutId))
    workout = workoutNames[workoutId]
    return workoutId, workout


def askAddWorkout():
    inVal = input('workout name:')
    return addWorkout(inVal)


def addWorkout(inVal):
    if inVal in workoutNames:
        workout = inVal
        workoutId = workoutNames.index(workout)
    else:
        addConfirm = input('Add workout "' + inVal + '"?(N/y) ')
        if addConfirm.lower() == 'y':
            workoutCategories = multiSelectOrAddCategories()

            global optionJsonData
            optionJsonData['workouts'].append({'Name': inVal, 'categories': workoutCategories})

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
                lastTimeStamp = getDatetimeFromStr(row[0])
                lastSameWorkoutHrs = (datetime.datetime.now() - lastTimeStamp).total_seconds()/60/60
                print("It's " + str(int(lastSameWorkoutHrs)) + ' hrs from last "' + workout + '"')
                lastRep = row[3]
                lastWeight = row[2]
                return lastTimeStamp, lastRep, lastWeight
    raise ValueError('no last record found for "' + workout + '"')

def getWeightAndRep(lastWeight, lastRep):
    weight = rep = ''

    inputs = input("weight(Kg)?(" + lastWeight + '), q to select new workout. ')
    # use last weight
    if inputs == '':
        inputs = lastWeight
    if inputs == 'q':
        raise UserCancelException

    inputs = inputs.split()
    weight = inputs[0]

    if len(inputs) == 2:
        rep = inputs[1]

    if rep == '':
        rep = input("rep?(" + lastRep + ") ")
        if rep == '':
            rep = lastRep
        if rep == 'q':
            raise UserCancelException
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


def selectWorkoutInFullList(lastWorkout):
    # print workout options
    printListWithId(workoutNames) 
    lastWorkoutValid = False
    lastWrokoutStr = ''
    try:
        lastWorkoutId = workoutNames.index(lastWorkout)
        lastWorkoutValid = True
        lastWrokoutStr = ' (' + str(lastWorkoutId) + ': ' + lastWorkout + ')'
    except Exception as e:
        pass   
    inVal = input('Which work out? q:exit, c: select by category, or enter the workout name to search or add' + lastWrokoutStr)
    processSelectorChange(inVal)
    # use last workout
    if inVal == '':
        if lastWorkoutValid:
            workoutId = lastWorkoutId
            workout = lastWorkout
        else:
            raise ValueError("last workout is invalid")
    elif inVal.isnumeric():
        workoutId, workout = selectWorkoutNumeric(inVal)
    else:
        workoutId, workout = addWorkout(inVal)
    return workoutId, workout


def checkIfThereIsNoWorkout():
    while len(workoutNames) == 0:
        inVal = input("please add first workout:")
        try:
            addWorkout(inVal)
        except Exception as e:
            print(e)


def main():
    readWorkoutOptions()

    # init last recorders
    lastWorkout = getLastWorkoutFromCsv()
    lastWeight = '0'
    lastRep = '20'
    lastTimeStamp = datetime.datetime.now()

    print("work out start at:" + lastTimeStamp.strftime(timeFormatString))

    # add first workout
    checkIfThereIsNoWorkout()
    
    while True:    
        try:
            workoutId, workout = selectWorkout(lastWorkout)
        except UserCancelException as e:
            continue
        except ValueError as e:
            print(e)
            continue

        lastWorkout = workout
        # get last same workout
        try:
            lastTimeStamp, lastRep, lastWeight = getLastSameWorkoutFromCsv(workout)
        except Exception as e:
            print(e)

        # get weight and rep
        while True:
            try:
                weight, rep = getWeightAndRep(lastWeight, lastRep)
            except UserCancelException as e:
                print(e)
                break
            
            timeStamp = datetime.datetime.now()
            printRecordAndWriteToCsv(timeStamp, workout, weight, rep, lastTimeStamp)

            lastRep = rep
            lastWeight = weight
            lastTimeStamp = timeStamp


if __name__ == '__main__':
    main()
