import mysql.connector



def connect_to_db():
    """
    function to connect to database
    :return: database connection
    """
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='my_password',
        port='3306',
        database='my_db'
    )
    return mydb


def get_members():
    """
    fetch members info from database into dictionary of members
    """
    members = []
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    mycursor.execute('select MemberId, MemberName from members')
    rows = mycursor.fetchall()

    # convert row objects to dictionary
    for i in rows:
        user = {}
        user["MemberId"] = i[0]
        user["MemberName"]= i[1]
        members.append(user)

    mydb.close()

    return members


def get_member(id):
    """
    fetch complete member info of id fro database to dictionary
    :param id: member id
    """
    member = {}
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    mycursor.execute(f"select * from members where MemberId= {id}")
    row = mycursor.fetchone()

    # convert row objects to dictionary
    member["MemberId"] = row[0]
    member["MemberName"]= row[1]
    member["MemberAddress"]= row[2]
    member["MemberBirth"]= row[3]
    member["MemberPhone"] = row[4]
    member["MemberMobile"] = row[5]

    mydb.close()
    return member


def get_covid_info(id):
    """
    get covid info of id member from database
    :param id: member id
    :return: doses : all the member doses detais, covid : member cotamination and recovery date
    """
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    #vaccine info
    mycursor.execute(f"select dose, doseDate, vaccineName from membervaccinedose inner join vaccine on membervaccinedose.vaccineId"
                     f"= vaccine.vaccineId where MemberId= {id}")
    rows = mycursor.fetchall()

    doses = []
    # convert row objects to dictionary
    for i in rows:
        dose = {}
        dose["dose"] = i[0]
        dose["doseDate"] = i[1]
        dose["vaccineName"] = i[2]
        doses.append(dose)

    # contamination and recovery dates
    mycursor.execute(f"select contaminationDate, recoveryDate from covid where MemberId={id}")
    covid = mycursor.fetchone()
    mydb.close()
    return doses, covid


def insert_member(member):
    """
    insert member into db
    :param member: dictionary of member info
    :return member details
    """
    inserted_member = {}
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO members (MemberId,MemberName,MemberAddress,MemberBirth,MemberPhone,MemberMobile) VALUES ( {member[0]},"
          f"\'{member[1]}\', \'{member[2]}\', \'{member[3]}\',{member[4]}, {member[5]})")
    conn.commit()
    conn.close()

    return get_member(member[0])


def update_member(member):
    """
    update member info to db
    :param member: member new info dict
    :return: new member info dict
    """
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    mycursor.execute(f"UPDATE members SET  MemberName = \'{member[1]}\', "
                     f"MemberAddress = \'{member[2]}\', MemberBirth = \'{member[3]}\', MemberPhone = {member[4]}, "
                     f"MemberMobile = {member[5]} where MemberId = {member[0]}")
    mydb.commit()
    updated_member = get_member(member[0])
    mydb.close()
    return updated_member


def delete_member(id):
    """
    delete member from db
    :param id: member id
    """
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    mycursor.execute(f"DELETE from members where MemberId = {id}")
    mydb.commit()

    mydb.close()


def get_vaccine(id):
    """
    get all the vaccines info that the member id has
    get all existing vaccines from db and their id code
    :param id: member id
    :return: min date of next vaccine, next dose, vaccine list
     or None if the member has arleady 4 doses
    """
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    # get member vaccine info
    mycursor.execute(f"select max(doseDate) + interval 1 day, count(*) from membervaccinedose where MemberId={id}")
    data = mycursor.fetchone()
    min_date = data[0]
    totaldose=data[1]
    if totaldose>3:
        return None

    # gets vaccines names list
    mycursor.execute(f"select * from vaccine")
    vaccines = mycursor.fetchall()
    mydb.close()
    return min_date,totaldose + 1, vaccines


def add_vaccine(doseinfo):
    """
    add new vaccine to db
    :param doseinfo: dose details dict (dose,doseDate,vaccineId,MemberId)
    """
    inserted_member = {}
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO membervaccinedose (dose,doseDate,vaccineId,MemberId) VALUES ( {doseinfo[0]},"
        f"\'{doseinfo[1]}\', \'{doseinfo[2]}\', \'{doseinfo[3]}\')")
    conn.commit()
    conn.close()


def add_contamination(id, contamination):
    """
    add contamination date to db
    :param id: member id
    :param contamination: date of contamination
    """
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute( f"INSERT INTO `nonotar`.`covid`(`MemberId`,`contaminationDate`) VALUES"
        f"({id},\'{contamination}\')")
    conn.commit()
    conn.close()


def add_recovery(id,recovery):
    """
       add recovery date to db
       :param id: member id
       :param recovery: date of recovery
       """
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE  `nonotar`.`covid` set recoveryDate=\'{recovery}\' where MemberId={id}")
    conn.commit()
    conn.close()


def add_image(id, binarydata):
    """
    add member image to db
    :param id: member id
    :param binarydata: img in bytes
    """
    conn =connect_to_db()
    cur = conn.cursor()
    if fetch_image(id) is None:
        cur.execute(f"INSERT INTO `nonotar`.`images`(`MemberId`,`photo`) VALUES (%s, %s)", (id,binarydata))
    else:
        cur.execute(f"update  `nonotar`.`images`set photo =%s where MemberId = {id}",(binarydata,))
    conn.commit()
    conn.close()


def fetch_image(id):
    """
    fetch member photo from db
    :param id:
    :return:
    """
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT photo from `nonotar`.`images` where MemberId = {id}")
    data = mycursor.fetchone()

    # if the member has no photo
    if data is None:
        return None
    image = data[0].decode('utf-8')
    mydb.commit()

    mydb.close()
    return image


def month_graph():
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    mycursor.execute(f"set @minDate = (current_date() - interval day(now()) - 1 day - interval 1 month)")
    mycursor.execute( f"set @MaxDate = (current_date() - interval day(now()) day)")
    for _ in mycursor.execute(f"with recursive cte (oneday) as ( select @minDate union all select (date(oneday) "
                     f"+ interval 1 day) from cte where oneday<@maxDate) "
                     f"select oneday, sum(sick) as "
                     f"totalsick from (select oneday, if (oneday between contaminationDate and "
                     f"recoveryDate,1,0) as sick from cte join covid) as s1 group by oneday "
                     f"order by oneday;", multi=True): pass
    month_data = mycursor.fetchall()
    return month_data


def total_unvaccinated():
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    mycursor.execute(f"select count(distinct(m.MemberId)) from members m where m.MemberId not in (select MemberId from membervaccinedose)")
    total = mycursor.fetchone()[0]
    return total

