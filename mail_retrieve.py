
##You need to import this to encode, decode, etc. 
import urllib.request, urllib.parse, urllib.error
import json
import ssl
import sqlite3
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


url = "https://data.pa.gov/resource/mcba-yywm.json"

conn = sqlite3.connect('mail_ballots.sqlite')
cur = conn.cursor()

cur.executescript('''
    DROP TABLE IF EXISTS Requests;
    DROP TABLE IF EXISTS Counties;
    DROP TABLE IF EXISTS Parties;
    DROP TABLE IF EXISTS Brackets;

    CREATE TABLE IF NOT EXISTS Requests(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        county_id INTEGER,
        party_id INTEGER,
        bracket_id INTEGER);

    CREATE TABLE IF NOT EXISTS Counties(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE);

    CREATE TABLE IF NOT EXISTS Parties(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE);

    CREATE TABLE IF NOT EXISTS Brackets(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE)
    ''')

run_type = input('Would you like to download the whole dataset? y/n ')

if run_type == 'n':
    records = int(input('How many records would you like to see? '))

    limit_num = records

    starting_place = input('Where would you like to start? ')

    if len(starting_place) == 0:
        starting_place = '0'
    
else:
    records = 3080000
    limit_num = 10000
    starting_place = '0'

limit = '?$limit=' + str(limit_num)

no_party = 0
no_dob = 0

count = 0

while count <= records:    
    
    offset = '&$offset=' + str(int(starting_place) + count)

    ##Creates the URL handle, ala a file handle.

    offset_url = url + limit + offset

    if count == 0:
        print('Retrieving',offset_url)
    
    uh = urllib.request.urlopen(offset_url, context = ctx)

    ##Decodes to unicode.
    
    data = uh.read().decode()

    ##Takes the string information and treats as JavaScript that needs converting
    ##into dictionaries, etc.
    
    info = json.loads(data)

    if(len(info)==0):
        break

    for item in info:
        
        county = item['countyname']

        age_divisions = ['18-19','20-29','30-39','40-49','50-59','60-69','70-79','80-89','90-99','100+']

        try:
            dob = item['dateofbirth']
            dob = dob[:4]
            int_dob = int(dob)

        #If their DOB is 1800, that means their DOB is masked
            if int_dob == 1800:
                bracket = 'Unknown'

            else:
                age = 2021 - int_dob

                index = (age // 10) - 1

        #If their age is over 100, keep the index at nine
                if index > 9:
                    index = 9

                bracket = age_divisions[index]
        except:
            no_dob = no_dob + 1
            bracket = 'Unknown'

        try:
            party = item['party']
        except:
            no_party = no_party + 1
            party = 'UNK'
              

        ##Input the county into its own table
    
        cur.execute('''INSERT OR IGNORE INTO Counties (name)
            VALUES (?)''',(county,))

        cur.execute('SELECT id FROM Counties WHERE name = ?',(county,))
        county_id = cur.fetchone()[0]

        ##Input the party into its own table

        cur.execute('''INSERT OR IGNORE INTO Parties (name)
            VALUES (?)''',(party,))

        cur.execute('SELECT id FROM Parties WHERE name = ?',(party,))
        party_id = cur.fetchone()[0]

        ##Input the brackets into its own table

        cur.execute('''INSERT OR IGNORE INTO Brackets (name)
            VALUES (?)''',(bracket,))

        cur.execute('SELECT id FROM Brackets WHERE name = ?',(bracket,))
        bracket_id = cur.fetchone()[0]
    

        ## Build the tables you'll point to first, so you have all the IDs
        ## When you go to insert it
        

        cur.execute('''INSERT INTO Requests (county_id, party_id, bracket_id)
            VALUES ( ?, ?, ?)''', (county_id, party_id, bracket_id))

        count = count + 1

        if count % 10000 == 0 :
            print('...')
            
    if count == records:
        break
            
    conn.commit()
        

print('Database updated with', count, 'records.')
print(no_party, 'records had no party.')
print(no_dob, 'records had no DOB.')
conn.commit()
cur.close()
