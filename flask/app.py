from flask import Flask, render_template, url_for, request
import os
import plotly.graph_objects as go
import plotly.io as pio
from pripojeni import *
import mysql.connector

mydb = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE
)

app = Flask(__name__)
app.secret_key = 'Muj_tajny_klic' # nazev pred route

@app.route('/1')
def home ():
    return "Ahoj, světe od ucitele!"

@app.route('/2')
def pozdarv_ze_souboru():
    return render_template("index2.html")

@app.route('/3')
def pozdarv_ze_souboru_CSS():
    return render_template("index3.html")

@app.route('/4')
def pozdarv_z_promenny():
    text= "Ahoj z proměnné"
    return render_template("index4.html", message = text)

@app.route('/5')
def obrazek():
    image_url = url_for('static', filename='vos-sps-kladno-logo-5.png')
    return render_template("index5.html", image_url=image_url)

@app.route('/6', methods=['GET', 'POST'])
def prvniFormularCislo():
    if request.method == 'POST':
        number = request.form.get('number', type=int)
        if number is not None:
            result = number + 1

    return render_template('index6.html', result=result)

app.config["UPLOAD_FOLDER"] = "static/uploadedFiles/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
@app.route('/7', methods=['GET', 'POST'])
def nahrani_souboru():
    content = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.txt'):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            file.seek(0)
            content = file.read().decode('utf-8')
    return render_template('index7.html', content=content)



@app.route('/8')
def graph():
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[10, 20, 25, 30],
        mode='lines+markers',
        name='Data 1'
    ))

    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[15, 18, 22, 27],
        mode='lines+markers',
        name='Data 2'
    ))

    fig.update_layout(
        title="Ukázkový interaktivní graf",
        xaxis_title="X-osa",
        yaxis_title="Y-osa",
        template="plotly_white"
    )

    graph_html = pio.to_html(fig, full_html=False)

    return render_template("index8.html", graph_html=graph_html)


@app.route('/9/cint:id>/<string:name>',methods=['GET'])
def parametry(id, name):
    return render_template("index9.html", id=id, name=name)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['jmeno']
        mail = request.form['email']
        psw = request.form['psw']

        # Hashování hesla
        hashed_password = bcrypt.hashpw(psw.encode('utf-8'), bcrypt.gensalt())
        hesloDoDB = hashed_password.decode('utf-8')

        # Připojení k DB
        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD, database=DATABASE
        )
        mycursor = mydb.cursor()

        # Vytvoření tabulky (pokud neexistuje)
        mycursor.execute("""CREATE TABLE IF NOT EXISTS uzivatele (
            id int AUTO_INCREMENT PRIMARY KEY,
            jmeno varchar(35) NOT NULL,
            email varchar(50) NOT NULL,
            heslo varchar(255) NOT NULL
        );""")
        mydb.commit()

        # Vložení uživatele
        sql = "INSERT INTO uzivatele (jmeno, email, heslo) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (name, mail, hesloDoDB))
        mydb.commit()

        return redirect(url_for('login'))  # po registraci → přihlášení

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']

        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD, database=DATABASE
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT heslo FROM uzivatele WHERE email = %s;", (email,))
        result = mycursor.fetchone()

        if result:
            stored_hash = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session['email'] = email  # uložení do session
                return redirect(url_for('home_login_ukazka'))
            else:
                error_message = "Nesprávné heslo."
        else:
            error_message = "Uživatel nenalezen."

        return render_template("login.html", error=error_message)

    return render_template("login.html")

@app.route('/home')
def home_login_ukazka():
    return render_template('home.html', email=session.get('email'))

# Route /logout — odhlášení uživatele
@app.route('/logout')
def logout():
    session.pop('email', None)  # odebrání ze session
    return redirect(url_for('home_login_ukazka'))

@app.route('/tabulka')
def tabulka():
    if 'email' not in session:
        return redirect(url_for('login'))  # ochrana stránky

    mydb = mysql.connector.connect(
        host=HOST, user=USER, password=PASSWORD, database=DATABASE
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM uzivatele")
    result = mycursor.fetchall()

    return render_template("tabulka.html", email=session.get('email'), items=result)

if __name__ == "__main__":
    app.run()
