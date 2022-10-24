import base64
import db_connector
from flask import Flask, request,render_template, redirect


app = Flask(__name__, template_folder='templates')


# for default route
@app.route("/")
def main():
    """
    display all members
    """
    members_list = db_connector.get_members()
    total = db_connector.total_unvaccinated()
    encoded = db_connector.month_graph()
    return render_template("members.html", members=members_list, total=total, encoded=encoded)


@app.route("/addmember", methods=['GET', 'POST'])
def add_member():
    """
    add member to database
    """
    if request.method == 'GET':
        return render_template("addmember.html", member={})

    if request.method == 'POST':
        new_member = []
        data = request.form
        new_member.append(int(data.get('id')))
        new_member.append(data.get('name'))
        new_member.append(data.get('address'))
        new_member.append(data.get('birth'))
        new_member.append(int(data.get('phone')))
        new_member.append(int(data.get('mobile')))
        db_connector.insert_member(new_member)

        # if the client inserted a photo
        if request.files is not None:
            f = request.files['photo']
            imgc = f.read()
            img = base64.b64encode(imgc)
            db_connector.add_image(int(data.get('id')), img)
        return redirect('/')


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    """
     display member info from db
     :param id: member id
     """
    member = db_connector.get_member(id)
    doses, covid = db_connector.get_covid_info(id)
    photo = db_connector.fetch_image(id)
    return render_template("memberdetails.html", member=member, doses=doses, covid=covid, photo=photo)


@app.route('/updatemember/<int:id>',  methods=['GET', 'POST'])
def update_member(id):
    """
     update member info from templates to db
     :param id: member id
     """
    if request.method == 'GET':
        member = db_connector.get_member(id)
        return render_template("addmember.html", member_id=id, member=member)
    # fetch form data
    if request.method == 'POST':
        member = [id]
        member.append(str(request.form['name']))
        member.append(str(request.form['address']))
        member.append(str(request.form['birth']))
        member.append(int(request.form['phone']))
        member.append(int(request.form['mobile']))
        db_connector.update_member(member)

        if request.files is not None:
            f = request.files['photo']
            imgc = f.read()
            img = base64.b64encode(imgc)
            db_connector.add_image(id, img)
        return redirect('/')


@app.route('/deletemember/<id>')
def delete_member(id):
    """
    delete member from db
    :param id:
    :return:
    """
    db_connector.delete_member(id)
    return redirect('/')


@app.route("/addvaccine/<id>", methods=['GET', 'POST'])
def add_vaccine(id):
    """
     input vaccine info from templates to db
     :param id: member id
     """
    if request.method == 'GET':
        min_date, dose, vaccines = db_connector.get_vaccine(id)

        # if there's already 4 vaccines registered
        if dose is None:
            return None
        return render_template("addvaccine.html", id=id, dose=dose, min_date=min_date, vaccines=vaccines)

    if request.method == 'POST':
        new_vaccine = []
        data = request.form
        new_vaccine.append(int(data.get('dose')))
        new_vaccine.append(data.get('doseDate'))
        new_vaccine.append(data.get('vaccineId'))
        new_vaccine.append(data.get('MemberId'))
        db_connector.add_vaccine(new_vaccine)
        return redirect('/')


@app.route("/addcontamination/<id>", methods=['GET', 'POST'])
def add_contamination(id):
    """
    input contamination info from templates to db
    :param id: member id
    """
    covid = db_connector.get_covid_info(id)[1]
    if covid is not None:
        return "contamination date already exists"
    if request.method == 'GET':
        return render_template("contaminationandrecovery.html", id=id, i=0)
    if request.method == 'POST':
        data = request.form
        contamination = data.get('contamination')
        db_connector.add_contamination(id, contamination)
        return redirect('/')


@app.route("/addrecovery/<id>", methods=['GET', 'POST'])
def add_recovery(id):
    """
       input recovery info from template to db
       :param id: member id
       """
    covid = db_connector.get_covid_info(id)[1]
    if covid is None or covid[1]:
        return "recovery date already exists or no contamination date yet"
    if request.method == 'GET':
        return render_template("contaminationandrecovery.html", id=id, contamination=covid[0], recovery=covid[1], i=1)

    if request.method == 'POST':
        data = request.form
        recovery = data.get('recovery')
        db_connector.add_recovery(id, recovery)
        return redirect('/')


@app.route("/addimage/<id>", methods=['GET', 'POST'])
def add_image(id):
    """
    fetch image from templates to db
    :param id: member id
    """
    if db_connector.fetch_image(id):
        return "image already uploaded"
    if request.method == 'GET':
        return render_template('addimage.html')
    if request.method == 'POST':
        f = request.files['photo']
        imgc = f.read()
        img = base64.b64encode(imgc)
        db_connector.add_image(id, img)
        return redirect('/')


if __name__ == "__main__":
    # run app
    app.run()
