from config import *
from werkzeug.exceptions import *
from flask import request, render_template, redirect, url_for

import flask_login

from datetime import datetime

from fileModel.fileInterface import FileSystemInterface as fsm
from fileModel.sessionInterface import SessionInterface as si
from tools.FileUtil import FileUtil

from model.User import User, users

def setChecked(data):
    data = json.loads(data)
    data['checked'] = True
    return json.dumps(data)

index = 0

def customExceptionHandler(fooName=None):
    def realHandler(foo):
        global index
        def inner(*args, **kwargs):
            try:
                return foo(*args, **kwargs)
            except HTTPException as httpe:
                return {request.path[1:]: False, 'data': {'description': 'HTTP error'}}, httpe.code
            except KeyError as jsone:
                return {request.path[1:]: False, 'data': {'description': f'Json error, lost {str(jsone.args[0]).upper()} param', 'param': jsone.args[0]}}, 200
            except Exception as e:
                return {request.path[1:]: False, 'data': {'description': 'Unmatched error', "error": type(e).__name__}}, 200
        if fooName:
            inner.__name__ = fooName
        else:
            inner.__name__ = "inner" + str(index)
            index += 1
        return inner
    return realHandler


# login functions
@login_manager.user_loader
def user_loader(login):
    if login not in users:
        return
    user = User()
    user.id = login
    return user

@login_manager.request_loader
def request_loader(request):
    login = request.form.get('login')
    if login not in users:
        return
    user = User()
    user.id = login
    return user

# controllers

# auth controllers 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', class_ ='', message='')

    login = request.form['login']
    if login in users and request.form['password'] == users[login]['password']:
        user = User()
        user.id = login
        flask_login.login_user(user)
        return redirect(url_for('getMain'))
    return render_template('login.html', class_ ='text-danger', message='Неверные данные')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html', class_ ='text-dark', message='Вы вышли из аккаунта')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', class_ ='', message='')

# main controllers

 
@app.route('/setNewWarning', methods=['GET', 'POST'])
@cross_origin()
@customExceptionHandler 
def setNewWarning():
    # {"client_name":"...", "type": "...", "img":"...", "screen":"...", "datetime": "..."}
    userName = request.json['client_name']
    warnType = request.json['type']
    # encImg1 = request.json['img']
    # encImg2 = request.json['screen']
    datetimestr = request.json['datetime']
    
    images = [FileUtil.convertBytesToImg(img) for img in request.json['images']]
    # img1 = FileUtil.convertBytesToImg(encImg1)
    # img2 = FileUtil.convertBytesToImg(encImg2)
    
    # if not img1 or not img2:
    #     return {'setNewWarning': False, 'data': {'description': 'bad image encoding'}}, 200
    warnDay, warnTime = datetimestr.split(' ')
    warnTime = warnTime.split('.')[0]
    print('exist:', fsm.checkExist(warnDay))
    if not fsm.checkExist(warnDay):
        fsm.createFolder('', warnDay)
        print('date f created')
    print('exsit2: ', fsm.checkExist(f'{warnDay}/{warnType}'))
    if not fsm.checkExist(f'{warnDay}/{warnType}'):
        fsm.createFolder(f'{warnDay}', f'{warnType}')
    
    
    # TODO: добавить проверку по группировке файлов
    
    if not fsm.checkExist(f'{warnDay}/{warnType}/{userName}'):
        fsm.createFolder(f'{warnDay}/{warnType}', f'{userName}')
        fsm.createFile(f'{warnDay}/{warnType}/{userName}/data.txt')
    
    
    def updateFileCounterInfo(data):
        if data != '':
            data = json.loads(data)
            data['counter'] += 1
        else:
            data = {'counter': 1}
            

        print('file data', data)
        return json.dumps(data)
    
    dataStr = fsm.doFileSystemJsonFileWorks(f'{warnDay}/{warnType}/{userName}/data.txt', updateFileCounterInfo)
    
    warnIndex = json.loads(dataStr)['counter']
    # новый индекс в типе ошибки за день
    # warnIndex = str(len(fsm.getFolderFiles(f'{warnDay}/{warnType}/{userName}')) + 1)
    fsm.createFolder(f'{warnDay}/{warnType}/{userName}', f'{warnIndex}')
    
    def updateFileInfo(data):
        if data != '':
            data = json.loads(data)
            data['begin'] = min(data['begin'], warnTime)
            data['end'] = max(data['end'], warnTime)
        else:
            data = {'begin': warnTime, 'end': warnTime, 'checked': False}
        return json.dumps(data)
    
    if not fsm.checkExist(f'{warnDay}/{warnType}/{userName}/{warnIndex}/data.txt'):
        fsm.createFile(f'{warnDay}/{warnType}/{userName}/{warnIndex}/data.txt')
    
    fsm.doFileSystemJsonFileWorks(f'{warnDay}/{warnType}/{userName}/{warnIndex}/data.txt', updateFileInfo)
    
    if not fsm.checkExist(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images'):
        fsm.createFolder(f'{warnDay}/{warnType}/{userName}/{warnIndex}', 'images')
    
    imgIndex = len(fsm.getFolderFiles(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images')) + 1
    for img in images:
        print( 'saving res1 is', fsm.saveImage(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images/img{imgIndex}.png', img))
        imgIndex += 1
    # print( 'saving res1 is', fsm.saveImage(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images/img{imgIndex}.png', img2))
    
    return {'setNewWarning': True}, 200



@app.route('/main', methods=['GET'])
@cross_origin()
@flask_login.login_required
@customExceptionHandler(fooName='getMain')  
def getMain():
    
    
    selectedUser = request.args.get('selectedUser')
    if not selectedUser:
        selectedImg = None
    selectedWarning = request.args.get('warnName')
    selectedImg = request.args.get('selectedImg') 
    if not selectedImg:
        selectedImg = ""
    selectedMonth = request.args.get('selectedMonth') 
    selectedDay = request.args.get('selectedDate') 
    if selectedMonth == 'None':
        selectedMonth = None
    if selectedDay == 'None':
        selectedDay = None
    selectedType = request.args.get('selectedType')
    if selectedType == 'None':
        selectedType = '0'
        
    onlyNew = request.args.get('onlyNew')
    if onlyNew == 'None' or onlyNew == None:
        onlyNew = 'false'
    
    if not selectedType:
        selectedType = '0'
            
    if selectedWarning:
        print(selectedWarning, fsm.checkExist(selectedWarning))
        if not fsm.checkExist(selectedWarning):
            selectedWarning = None
            # if not selected
            if selectedUser and selectedDay and selectedMonth:
                if selectedType != '0':
                    print(f'{selectedMonth}-{selectedDay}/{selectedType}/{selectedUser}', fsm.checkExist(f'{selectedMonth}-{selectedDay}/{selectedType}/{selectedUser}'))
                    if not fsm.checkExist(f'{selectedMonth}-{selectedDay}/{selectedType}/{selectedUser}'):
                        selectedUser = None
                        print(f'setting user none ({selectedType})')
                        if not fsm.checkExist(f'{selectedMonth}-{selectedDay}/{selectedType}'):
                            selectedDay = None
                else:
                    print(f'{selectedMonth}-{selectedDay}/1/{selectedUser}', fsm.checkExist(f'{selectedMonth}-{selectedDay}/1/{selectedUser}'))
                    print(f'{selectedMonth}-{selectedDay}/2/{selectedUser}', fsm.checkExist(f'{selectedMonth}-{selectedDay}/2/{selectedUser}'))
                    if not ( fsm.checkExist(f'{selectedMonth}-{selectedDay}/1/{selectedUser}') or fsm.checkExist(f'{selectedMonth}-{selectedDay}/2/{selectedUser}')):
                        print('setting user none (0)')
                        selectedUser = None
                        if not( fsm.checkExist(f'{selectedMonth}-{selectedDay}/1') or fsm.checkExist(f'{selectedMonth}-{selectedDay}/2') ):
                            selectedDay = None
                            
    
        
    warnings = {}
    allUsers = {}
    datesDict = {}
    imagesList = []
    warningDates = {}
    warnData = ''
    dates = fsm.getFolderFiles('')
    for date in dates:
        if selectedMonth:
            if selectedDay:
                print('comp', date, selectedMonth+'-'+selectedDay)
                if date != selectedMonth+'-'+selectedDay:
                    print('passing')
                    continue
            else:
                print('comp', date[:7], selectedMonth)
                if date[:7] != selectedMonth:
                    print('passing')
                    continue
        count = 0
        if date == 'system':
            continue
        datesDict[date] = {}
        types = fsm.getFolderFiles(date)
        for tp in types:
            if selectedType != '0':
                if selectedType != tp:
                    continue
            datesDict[date][tp] = {}
            users = fsm.getFolderFiles(f'{date}/{tp}')
            for user in users:
                if not(user in allUsers):
                    allUsers[user] = False # notChecked
                datesDict[date][tp][user] = {}
                cases = fsm.getFolderFiles(f'{date}/{tp}/{user}')
                for cs in cases:
                    i = 0
                    if cs != 'data.txt':
                        
                        
                        data = json.loads(fsm.readFileSystemTxt(f'{date}/{tp}/{user}/{cs}/data.txt'))
                        datesDict[date][tp][user][cs] = {
                                                        'images':[f'{date}/{tp}/{user}/{cs}/images/{name}' for name in fsm.getFolderFiles(f'{date}/{tp}/{user}/{cs}/images')],
                                                        'data': data
                                                        }
                        if onlyNew == 'false' or not data['checked']:
                            count += 1
                            
                        if not data['checked']:
                            allUsers[user] = True
                        if selectedWarning == f'{date}/{tp}/{user}/{cs}':
                            fsm.doFileSystemJsonFileWorks(f'{date}/{tp}/{user}/{cs}/data.txt', setChecked)
                            datesDict[date][tp][user][cs]['data']['checked'] = True
                            imagesList = datesDict[date][tp][user][cs]['images']
                            warnData = f'Пользователь: {user} Продолжительность: {datesDict[date][tp][user][cs]["data"]["begin"]} - {datesDict[date][tp][user][cs]["data"]["end"]}'
                        print(selectedUser, user)
                        if selectedUser == user:
                            print('here')
                            if onlyNew == 'true':
                                if datesDict[date][tp][user][cs]['data']['checked']:
                                    continue
                            warnings[f'{date} {data["begin"]}|{cs}|type: {tp}'] = {'route': f'{date}/{tp}/{user}/{cs}', 'notChecked': not datesDict[date][tp][user][cs]['data']['checked']}
        
        warningDates[date] = [count, date[:-3], date[-2:]]    
    
    newWarningDates = {}
    for dt in warningDates:
        if warningDates[dt][0] != 0:
            newWarningDates[dt] = warningDates[dt]
    warningDates = newWarningDates   
              
    if selectedImg == "" and len(imagesList):
        selectedImg = imagesList[0]
    
    if onlyNew == 'true':
        newAllUsers ={}
        for u in allUsers:
            if allUsers[u]:
                newAllUsers[u] = True
        allUsers = newAllUsers
    sortedWarns = {}
    for k in sorted(warnings):
        sortedWarns[k] = [warnings[k]['route'], warnings[k]['notChecked']]
    # print('warns', sorted(warnings))
    # print(datesDict)
    return render_template('main.html',  users=allUsers, selectedUser=selectedUser, 
                                         warnings=sortedWarns, selectedWarning=selectedWarning, 
                                         imagesList=imagesList, selectedImg=selectedImg,
                                         warningDates=warningDates, warnData=warnData,
                                         selectedMonth=selectedMonth, selectedDate=selectedDay,
                                         selectedType=selectedType, onlyNew=onlyNew)
    
    
@app.route('/deleteWarn', methods=['GET'])
@cross_origin()
@flask_login.login_required
@customExceptionHandler(fooName='deleteWarn')  
def deleteWarn():
    # example: 2023-10-15/2/user1/4
    warnName = request.args.get('warnName')
    # request.args.pop('warnName')
    if warnName:
        day, tp, user, ind = warnName.split('/')
        fsm.delete(warnName)
        if len( fsm.getFolderFiles(f'{day}/{tp}/{user}')) <= 1:
            fsm.delete(f'{day}/{tp}/{user}')
            if len( fsm.getFolderFiles(f'{day}/{tp}')) == 0:
                fsm.delete(f'{day}/{tp}')
                if len( fsm.getFolderFiles(f'{day}')) == 0:
                    fsm.delete(f'{day}')
        return getMain()
    return {'delete': False, 'data': {'message': 'Bad WARNNAME param'}}, 200
                    
    
            
    