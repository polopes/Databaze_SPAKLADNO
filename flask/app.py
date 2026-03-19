from flask import Flask, render_template, url_for, request
import os

app = Flask(__name__) # nazev pred route

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


if __name__ == '__main__':
    app.run()

