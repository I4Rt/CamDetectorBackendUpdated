from config import *
from werkzeug.exceptions import *
from flask import request, render_template


from datetime import datetime

from fileModel.fileInterface import FileSystemInterface as fsm
from tools.FileUtil import FileUtil



def setChecked(data):
    data = json.loads(data)
    data['checked'] = True
    return json.dumps(data)

index = 0
def customExceptionHandler(foo):
    global index
    def inner(*args, **kwargs):
        try:
            return foo(*args, **kwargs)
        except HTTPException as httpe:
            return {request.path[1:]: False, 'data': {'description': 'HTTP error'}}, httpe.code
        except KeyError as jsone:
            return {request.path[1:]: False, 'data': {'description': f'Json error, lost {str(jsone.args[0]).upper()} param', 'param': jsone.args[0]}}, 200
        # except Exception as e:
        #     return {request.path[1:]: False, 'data': {'description': 'Unmatched error', "error": type(e).__name__}}, 200
    inner.__name__ = "inner" + str(index)
    index += 1
    return inner


 
@app.route('/setNewWarning', methods=['GET', 'POST'])
@cross_origin()
@customExceptionHandler 
def setNewWarning():
    # {"client_name":"...", "type": "...", "img":"...", "screen":"...", "datetime": "..."}
    userName = request.json['client_name']
    warnType = request.json['type']
    encImg1 = request.json['img']
    encImg2 = request.json['screen']
    datetimestr = request.json['datetime']
    img1 = FileUtil.convertBytesToImg(encImg1)
    img2 = FileUtil.convertBytesToImg(encImg2)
    
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
    print( 'saving res1 is', fsm.saveImage(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images/img{imgIndex}.png', img1))
    imgIndex += 1
    print( 'saving res1 is', fsm.saveImage(f'{warnDay}/{warnType}/{userName}/{warnIndex}/images/img{imgIndex}.png', img2))
    
    return {'setNewWarning': True}, 200



@app.route('/main', methods=['GET'])
@cross_origin()
@customExceptionHandler    
def main():
    
    
    selectedUser = request.args.get('selectedUser')
    selectedWarning = request.args.get('warnName')
    selectedImg = request.args.get('selectedImg') 
    if not selectedImg:
        selectedImg = ""
    warnings = {}
    allUsers = {}
    datesDict = {}
    imagesList = []
    dates = fsm.getFolderFiles('')
    for date in dates:
        if date == 'system':
            continue
        datesDict[date] = {}
        types = fsm.getFolderFiles(date)
        for tp in types:
            datesDict[date][tp] = {}
            users = fsm.getFolderFiles(f'{date}/{tp}')
            for user in users:
                if not(user in allUsers):
                    allUsers[user] = False # notChecked
                datesDict[date][tp][user] = {}
                cases = fsm.getFolderFiles(f'{date}/{tp}/{user}')
                for cs in cases:
                    if cs != 'data.txt':
                        data = json.loads(fsm.readFileSystemTxt(f'{date}/{tp}/{user}/{cs}/data.txt'))
                        datesDict[date][tp][user][cs] = {
                                                        'images':[f'{date}/{tp}/{user}/{cs}/images/{name}' for name in fsm.getFolderFiles(f'{date}/{tp}/{user}/{cs}/images')],
                                                        'data': data
                                                        }
                        
                        allUsers[user] = max(not data['checked'], False)
                        print(selectedWarning, f'{date}/{tp}/{user}/{cs}')
                        if selectedWarning == f'{date}/{tp}/{user}/{cs}':
                            fsm.doFileSystemJsonFileWorks(f'{date}/{tp}/{user}/{cs}/data.txt', setChecked)
                            datesDict[date][tp][user][cs]['data']['checked'] = True
                            imagesList = datesDict[date][tp][user][cs]['images']
                        if selectedUser == user:
                            warnings[f'{date} {data["begin"]} | type: {tp}'] = {'route': f'{date}/{tp}/{user}/{cs}', 'notChecked': not datesDict[date][tp][user][cs]['data']['checked']}
                            
    
    
    sortedWarns = {}
    for k in sorted(warnings):
        sortedWarns[k] = [warnings[k]['route'], warnings[k]['notChecked']]
    # print('warns', sorted(warnings))
    print(datesDict)
    return render_template('main.html',  users=allUsers, selectedUser=selectedUser, warnings=sortedWarns, selectedWarning=selectedWarning, imagesList=imagesList, selectedImg=selectedImg)