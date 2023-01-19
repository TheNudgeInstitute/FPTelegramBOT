from DB_class import DynamoDB_con

import datetime

DB = DynamoDB_con()


sessionData, totalSess = DB.read_read('TB_Temp_JumbledWord_Session')


def UpdateTheData():
    print('running set time function!')

    total_sum_points = {}
    for dic in sessionData:
        if dic['User_Id'] not in total_sum_points:

            total_sum_points[dic['User_Id']] = {'Points_Scored': int(
                dic["Points_Scored"]), 'Datetime': dic['Datetime'], 'JumbledWord_Participation': 1}
        else:
            total_sum_points[dic['User_Id']
                             ]['Points_Scored'] += int(dic["Points_Scored"])
            total_sum_points[dic['User_Id']]['JumbledWord_Participation'] += 1

    for dic in total_sum_points:
        data = {"User_id": str(dic), "date": str(datetime.datetime.now()), "JumbledWord_Points": str(
            total_sum_points[dic]['Points_Scored']), "JumbledWord_Participation": str(total_sum_points[dic]['JumbledWord_Participation'])}
        DB.send_data(data, 'TB_User_Points')
    DB.deleteTotalData()
