import sqlite3
import pandas as pd

def menu():
    select = input('''What would you like to do?
                    1. Count by Party
                    2. Count by County
                    3. Count by Age Bracket
                    ''')
    
    if select == '1':
        count_by_Party()

    if select == '2':
        count_by_County()

    if select == '3':
        count_by_Bracket()

def count_by_Party():
    
    conn = sqlite3.connect('mail_ballots.sqlite')
    cur = conn.cursor()

    sqlstr = '''SELECT Parties.name from Parties'''

    parties_dic = {}
    parties_list = []

    for party in cur.execute(sqlstr):
        parties_dic[party[0]] = 0
        parties_list.append(party[0])
    
    sqlstr = '''SELECT Parties.name from Parties join Requests on Requests.party_id = Parties.id'''

    for line in cur.execute(sqlstr):
        parties_dic[line[0]] = parties_dic[line[0]] + 1

    count = 0

    sorted_parties = []

    for party in parties_list:
        str_party = str(party)
        records = parties_dic[party]
        count = count + records
        tup = (records, party)
        sorted_parties.append(tup)

    sorted_parties.sort(reverse = True)

    l = len(parties_dic)
    l_str = str(l)
    print('(Data for '+l_str+' parties is available.)')

    stop = int(input('How many individual parties to display? '))
    top = 0
    other = 0
    
    x = []
    y = []
    ystr = []
    
    for tup in sorted_parties:
        if top < stop:
            percent = "{:.0%}".format(tup[0] / count)
            print(str(tup[1]) + ': ' + str(tup[0]) + ' - ' + percent)
            x.append(tup[1])
            ystr.append(percent)
            top = top + 1
            
        else:
            other = other + tup[0]

    other_percent = "{:.0%}".format(other / count)
    

    x.append('Other')
    ystr.append(other_percent)

    print('Other: ' + str(other) + ' - ' + other_percent)

    for item in ystr:
        num = int(item[:-1])
        y.append(num)

    print(x)
    print(y)

    df = pd.DataFrame({'Parties':x, 'Percentage':y})
    df.head()
    ax = df.plot.bar(x='Parties', y='Percentage', rot=0)


def count_by_County():

    conn = sqlite3.connect('mail_ballots.sqlite')
    cur = conn.cursor()

    sqlstr = '''SELECT Counties.name from Counties'''

    counties_dic = {}
    counties_list = []

    for county in cur.execute(sqlstr):
        counties_dic[county[0]] = 0
        counties_list.append(county[0])
        
    sqlstr = '''SELECT Counties.name from Counties join Requests on Requests.county_id = Counties.id'''

    for line in cur.execute(sqlstr):
        counties_dic[line[0]] = counties_dic[line[0]] + 1

    count = 0

    sorted_counties = []

    for county in counties_list:
        str_county = str(county)
        records = counties_dic[county]
        count = count + records
        tup = (records,county)
        sorted_counties.append(tup)

    sorted_counties.sort(reverse = True)

    l = len(counties_dic)
    l_str = str(l)
    print('(Data for '+l_str+' counties is available.)')
    
    stop = int(input('How many individual counties to display? '))
    top = 0
    other = 0
    
    x = []
    y = []
    ystr = []
    
    for tup in sorted_counties:
        if top < stop:
            percent = "{:.0%}".format(tup[0] / count)
            print(str(tup[1]) + ': ' + str(tup[0]) + ' - ' + percent)
            x.append(tup[1])
            ystr.append(percent)
            top = top + 1
            
        else:
            other = other + tup[0]

    other_percent = "{:.0%}".format(other / count)

    x.append('Other')
    ystr.append(other_percent)

    for item in ystr:
        num = int(item[:-1])
        y.append(num)

    print(x)
    print(y)
    print('Other: ' + str(other) + ' - ' + other_percent)

    df = pd.DataFrame({'Counties':x, 'Percentage':y})
    df.head()
    ax = df.plot.bar(x='Counties', y='Percentage', rot=0)

def count_by_Bracket():

    conn = sqlite3.connect('mail_ballots.sqlite')
    cur = conn.cursor()

    sqlstr = '''SELECT Brackets.name from Brackets'''

    bracket_dic = {}
    bracket_order_dic = {}
    bracket_order = []

    for bracket in cur.execute(sqlstr):
        str_bracket = bracket[0]
        try:
            low_bound = int(str_bracket[0:2])
        except:
            low_bound = 101
        if low_bound == 18:
            low_bound = 1
        if low_bound == 10:
            low_bound = 100
        bracket_dic[bracket[0]] = 0
        bracket_order_dic[low_bound] = bracket[0]
        bracket_order.append(low_bound)

    bracket_order.sort()
       
    sqlstr = '''SELECT Brackets.name from Brackets join Requests on Requests.bracket_id = Brackets.id'''

    count = 0
    
    for line in cur.execute(sqlstr):
        bracket_dic[line[0]] = bracket_dic[line[0]] + 1
        count = count + 1

    sorted_brackets = []

    x = []
    y = []
    ystr = []
    
    for item in bracket_order:
        bracket = bracket_order_dic[item]
        records = bracket_dic[bracket]
        percent = "{:.0%}".format(records / count)
        print(str(bracket) + ': ' + str(records) + ' - ' + percent)
        x.append(bracket)
        ystr.append(percent)

    for item in ystr:
        num = int(item[:-1])
        y.append(num)
    
    df = pd.DataFrame({'Brackets':x, 'Percentage':y})
    df.head()
    ax = df.plot.bar(x='Brackets', y='Percentage', rot=0)
    
if __name__ == '__main__':
    menu()



