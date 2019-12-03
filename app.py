from flask import Flask, render_template, redirect, url_for, request
from spotifyApi import SpotifyAPI
from forms import UsersForm

app=Flask(__name__)
app.config['SECRET_KEY'] = 'testing'


@app.route("/", methods=['GET', 'POST'])
def index():
    form = UsersForm()
    if form.validate_on_submit():
        result = request.form
        input_selection = result.get('input_type')
        if input_selection == 'username':
            user1 = result.get('user1')
            user2 = result.get('user2')
        else:
            user1 = result.get('user1')
            user1 = user1.split('?')[0].split('/')[-1]
            user2 = result.get('user2')
            user2 = user2.split('?')[0].split('/')[-1]
        return redirect('/result/{}/{}/'.format(user1, user2))
    return render_template('userinput.html', form=form)

@app.route('/result/<user1>/<user2>/', methods=['GET', 'POST'])
def next(user1, user2):
    sp = SpotifyAPI()
    gp1, name1 = sp.get_genre_profile(user1)
    gp2, name2 = sp.get_genre_profile(user2)
    difference = sp.compare_genre_profiles(gp1, gp2) * 100
    difference = round(difference, 3)

    top5genres1 = []
    data51 = []
    top5genres2 = []
    data52 = []
    for i in range(5):
        top5genres1.append(str(gp1[i][0]))
        data51.append(float(gp1[i][1]))
        top5genres2.append(str(gp2[i][0]))
        data52.append(float(gp2[i][1]))
    return render_template('resultview.html', results1=gp1, results2=gp2, difference=difference, name1=name1, name2=name2, topgenres1=top5genres1, data1=data51, topgenres2=top5genres2, data2=data52)
