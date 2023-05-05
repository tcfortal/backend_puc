from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'



swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)


user = os.getenv("DATABASE_PASS")
database = os.getenv("DATABASE_NAME")



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + database + ':' + user + '@localhost/BancoPuc'
db = SQLAlchemy(app)
CORS(app)




class Event(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    description = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __repr__(self):
         return f"Event: {self.description}"


    def __init__(self, description):
         self.description = description


def format_event(event):
    return {
        "description": event.description,
        "id": event.id,
        "created_at": event.created_at
    }



@app.route('/')
def hello():
    return 'Hey'




#criando um evento
@app.route('/events', methods =['POST'])
def create_event():
    description = request.json['description']
    event = Event(description)
    db.session.add(event)
    db.session.commit()
    return format_event(event)



#pegar todos os eventos
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.order_by(Event.created_at.asc()).all()
    event_list = []
    for event in events:
         event_list.append(format_event(event))
    return{'events': event_list}
    


#pegar um unico evento
@app.route('/events/<id>', methods=['GET'])
def get_event(id):
    event = Event.query.filter_by(id=id).one()
    formatted_event = format_event(event)
    return {'event': formatted_event}



#deletar um evento
@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.filter_by(id=id).one()
    db.session.delete(event)
    db.session.commit()
    return f'Event (id: {id}) deleted!'



#atualizar evento                                  
@app.route('/events/<id>', methods=['PUT'])
def update_event(id):
    event = Event.query.filter_by(id=id)
    description = request.json['description']
    event.update(dict(description = description, created_at = datetime.utcnow()))
    db.session.commit()
    return {'event': format_event(event.one())}



if __name__ == '__main__':
    app.run()

