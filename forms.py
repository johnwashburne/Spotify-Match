from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError

def check_spotify_url(form, field):
    user = field.data
    user = user.split('?')
    if len(user) != 2:
        raise ValidationError('Must paste a valid spotify user link')
    elif 'spotify' not in user[0]:
        raise ValidationError('Must paste a valid spotify user link')

# https://open.spotify.com/user/6dyaekf6k7z6yfkfn3qwyug3h?si=FwvcYyguTzmRPSdzpqQY8Q

class UsersForm(FlaskForm):
    user1 = StringField('User 1', validators=[DataRequired(), check_spotify_url])
    user2 = StringField('User 2', validators=[DataRequired(), check_spotify_url])
