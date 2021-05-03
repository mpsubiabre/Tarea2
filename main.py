from flask import Flask, render_template, request, jsonify
from flask_restful import Api, Resource
from flask_mysqldb import MySQL
import yaml
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode
import json
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/data.db'
db = SQLAlchemy(app)

############## MODELOS #############################

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))

class Artista(db.Model):
    id = db.Column(db.Text(22), primary_key = True)
    name = db.Column(db.Text(200))
    age = db.Column(db.Integer)
    album = db.Column(db.Text(200))
    tracks = db.Column(db.Text(200))
    self_url = db.Column(db.Text(200))
    owner_album = db.relationship('Album',cascade='all,delete',backref='artistowner')

class Album(db.Model):
    id = db.Column(db.Text(22), primary_key = True)
    artist_id = db.Column(db.Text(22), db.ForeignKey('artista.id'))
    name = db.Column(db.Text(200))
    genre = db.Column(db.Text(200))
    artist = db.Column(db.Text(200))
    tracks = db.Column(db.Text(200))
    self_url = db.Column(db.Text(200))
    owner_cancion = db.relationship('Cancion', cascade='all,delete',backref='albumowner')

class Cancion(db.Model):
    id = db.Column(db.Text(22), primary_key = True)
    album_id = db.Column(db.Text(22), db.ForeignKey('album.id'))
    name = db.Column(db.Text(200))
    duration = db.Column(db.Float)
    times_played = db.Column(db.Integer)
    artist = db.Column(db.Text(200))
    album = db.Column(db.Text(200))
    self_url = db.Column(db.Text(200))


############## FUNCIONES #############################
def cut_codification(a):
    print(a, len(a))
    if len(a) > 22:
        a = a[:22]
    print(a, len(a))
    return a

############## RUTAS #############################

@app.route('/', methods=['GET'])
def index():
    print('holaa')
    return render_template('app.html')

###################### ARTISTA #############################



@app.route('/artists', methods=['POST'])
def create_artist():
    print(request.is_json)
    data = request.get_json()
    key = data.keys()
    llaves = []
    for i in key:
        llaves.append(i)
    key0 = llaves[0]
    key1 = llaves[1]
    if key0 != 'name' or key1 != 'age':
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400
    
    print(type(key0), type(key1))

    if type(data['name']) != str or type(data['age'])!=int:
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400
    name = data['name']
    age = data['age']
    print(name, age)
    #codificar
    encoded_name = b64encode(name.encode()).decode('utf-8')
    encoded_name = cut_codification(encoded_name)
    
    path_album = '/artists/'+ encoded_name +'/albums'
    path_track = '/artists/'+ encoded_name +'/tracks'
    path_self = '/artists/'+ encoded_name

    try:
        artista = Artista(id= encoded_name, name = name, age = age, album = path_album, tracks = path_track, self_url = path_self)
        db.session.add(artista)
        db.session.commit()
        data = 'artista creado'

    except IntegrityError:
        db.session.rollback()
        i = Artista.query.get(encoded_name)
        print('Existe')
        dicc = {'id':i.id, 'name':i.name, 'age':i.age, 'albums':i.album, 'tracks':i.tracks, 'self':i.self_url}
        return json.dumps(dicc, ensure_ascii=False), 409
    except DataError:
        print("data")
    except KeyError:
        print("data")

    return json.dumps(data), 201

@app.route('/artists', methods=['GET'])
def get_artistas():
    all_artistas = Artista.query.all()
    all = []
    print(all_artistas)
    for i in all_artistas:
        dicc = {'id':i.id, 'name':i.name, 'age':i.age, 'albums':i.album, 'tracks':i.tracks, 'self':i.self_url}
        all.append(dicc)
    print(all)
    print("aca", json.dumps(all))
    return json.dumps(all, ensure_ascii=False), 200



@app.route('/artists/<artist_id>', methods=['GET'])
def create_artist2(artist_id):
    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista no existe'
        return json.dumps(data, ensure_ascii=False), 422
    else:
        dicc = {'id':k.id, 'name':k.name, 'age':k.age, 'albums':k.album, 'tracks':k.tracks, 'self':k.self_url}
        return json.dumps(dicc, ensure_ascii=False), 200

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista inexistente'
        return json.dumps(data, ensure_ascii=False), 404
    else:
        artist = Artista.query.get(artist_id)
        print(artist)
        albums = Album.query.filter_by(artist_id=artist_id).all()
        print(f'Existen {len(albums)} albums')

        for album in albums:
            print(f'id album: ', album.id)
            print(f'nombre album: ', album.name)
            idalbum = album.id
            canciones = Cancion.query.filter_by(album_id = album.id).all()
            print(f'Existen {len(canciones)} canciones')
            for cancion in canciones:
                print(f'nombre cancion {cancion.name}')
                Cancion.query.filter_by(id = cancion.id).delete()
                db.session.commit()
                print('CANCION BORRADA') 
            canciones = Cancion.query.filter_by(album_id = album.id).all()
            print(f'Existen {len(canciones)} canciones')       
            Album.query.filter_by(id = album.id).delete()
            db.session.commit()
            print('ALBUM BORRADO')
            
            albumes = Album.query.filter_by(artist_id=artist_id).all()
            print(f'Existen {len(albumes)} albums')
            cancion = Cancion.query.filter_by(album_id = idalbum).all()
            print(f'Existen {len(canciones)} canciones')
            for i in cancion:
                print('NO DEBERIA ENTRAR')
                print(i.name)
            print('\n')
        print('FINNNNNNNNNNNNNNNNN')
        artist = Artista.query.get(artist_id)
        print(artist)
        Artista.query.filter_by(id=artist_id).delete()
        artist = Artista.query.get(artist_id)
        print(artist)
        db.session.commit()
        data = 'artista eliminado'
        return json.dumps(data, ensure_ascii=False), 204
    return json.dumps(data, ensure_ascii=False), 204
    

###################### ALBUMS #############################

@app.route('/artists/<artist_id>/albums', methods=['GET'])
def create_album(artist_id):
    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista no encontrado'
        return json.dumps(data, ensure_ascii=False), 422
    else:
        buscar_album = Album.query.filter_by(artist_id=artist_id).all()
        all = []
        for i in buscar_album:
            dicc={'id' : i.id, 'name': i.name, 'genre' : i.genre, 'artist' : i.artist, 'tracks':i.tracks, 'self': i.self_url}
            all.append(dicc)
            print(i.name)
        print(all)
        print("INPUT ALBUM ", buscar_album)
        return json.dumps(all, ensure_ascii=False), 200

@app.route('/artists/<artist_id>/albums', methods=['POST'])
def create_album_database(artist_id):
    data = request.get_json()
    key = data.keys()

    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista no existe'
        return json.dumps(data, ensure_ascii=False), 422
        
    llaves = []
    for i in key:
        llaves.append(i)
    key0 = llaves[0]
    key1 = llaves[1]
    if key0 != 'name' or key1 != 'genre':
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400
    
    print(type(key0), type(key1))
    print(key0, key1)
    print(type(data['name']), type(data['genre']))
    print(data['name'], data['genre'])

    if type(data['name']) != str or type(data['genre']) != str:
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400

    name = data['name']
    genre = data['genre']

    #codificar
    codi = name+':'+ artist_id
    encoded_name = b64encode(codi.encode()).decode('utf-8')
    encoded_name = cut_codification(encoded_name)

    path_artist = '/artists/'+ artist_id
    path_track = '/albums/'+ encoded_name +'/tracks'
    path_self = '/artists/'+ artist_id + '/albums'

    try:
        album = Album(id= encoded_name, artist_id = artist_id, name = name, genre = genre, artist = path_artist, tracks = path_track, self_url = path_self)
        db.session.add(album)
        db.session.commit() 
        data = 'se creo un album'

    except IntegrityError:
        db.session.rollback()
        i = Album.query.get(encoded_name)
        print('Existe')
        dicc={'id' : i.id, 'name': i.name, 'genre' : i.genre, 'artist' : i.artist, 'tracks':i.tracks, 'self': i.self_url}
        return json.dumps(dicc, ensure_ascii=False), 409
    except DataError:
        print("data")
    except KeyError:
        print("data")
    
    return json.dumps(data, ensure_ascii=False), 201


@app.route('/albums', methods=['GET'])
def get_albums():
    all_albums = Album.query.all()
    print(all_albums)
    all = []
    for i in all_albums:
        #j = jsonify(id = i.id, name=i.name, genre= i.genre, artist= i.artist, tracks=i.tracks, self = i.self_url)  
        dicc={'id' : i.id, 'name': i.name, 'genre' : i.genre, 'artist' : i.artist, 'tracks':i.tracks, 'self': i.self_url}
        all.append(dicc)
    print(all)
    print("aca", json.dumps(all))
    return json.dumps(all, ensure_ascii=False), 200

@app.route('/albums/<album_id>', methods=['GET'])
def obtener_album(album_id):
    k = Album.query.get(album_id)
    if k == None:
        data = 'álbum no encontrado'
        return json.dumps(data, ensure_ascii=False), 404
    else:
        i = Album.query.get(album_id)   
        dicc={'id' : i.id, 'name': i.name, 'genre' : i.genre, 'artist' : i.artist, 'tracks':i.tracks, 'self': i.self_url}
        return json.dumps(dicc, ensure_ascii=False), 200


@app.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(album_id):
    print('borran2')

    k = Album.query.get(album_id)
    if k == None:
        data = 'álbum no encontrado'
        return json.dumps(data, ensure_ascii=False), 404
    else:
        album = Album.query.get(album_id)
        print(f'id album: ', album.id)
        print(f'nombre album: ', album.name)
        idalbum = album.id
        canciones = Cancion.query.filter_by(album_id = album.id).all()
        print(f'Existen {len(canciones)} canciones')
        for cancion in canciones:
            print(f'nombre cancion {cancion.name}')
            Cancion.query.filter_by(id = cancion.id).delete()
            db.session.commit()
            print('CANCION BORRADA') 
        canciones = Cancion.query.filter_by(album_id = album.id).all()
        print(f'Existen {len(canciones)} canciones')       
        Album.query.filter_by(id = album.id).delete()
        db.session.commit()
        print('ALBUM BORRADO')
        
        #  Album.query.filter_by(artist_id=artist_id).delete()
        album = Album.query.get(album_id)
        print(album)
        cancion = Cancion.query.filter_by(album_id = album_id).all()
        print(f'Existen {len(canciones)} canciones')
        for i in cancion:
            print('NO DEBERIA ENTRAR')
            print(i.name)
        data = 'álbum eliminado'
        return json.dumps(data, ensure_ascii=False), 204
    return json.dumps(data, ensure_ascii=False), 204


###################### TRACKS #############################

@app.route('/albums/<album_id>/tracks', methods=['GET'])
def create_cancion(album_id):
    k = Album.query.get(album_id)
    if k == None:
        data = 'álbum no encontrado'
        return json.dumps(data, ensure_ascii=False), 404
    else:
        album = Album.query.get(album_id)        
        buscar_track = Cancion.query.filter_by(album_id=album_id).all()
        all = []
        for i in buscar_track:
            dicc={'id' : i.id, 'album_id': i.album_id, 'name': i.name, 'duration' : i.duration, 'artist' : i.artist, 'album': i.album, 'self': i.self_url}
            print('info_track', i.album_id, i.name)
            print('/n\n')
            all.append(dicc)
        print(all)
        print('se imprimen los tracks')
        return json.dumps(all, ensure_ascii=False), 200

@app.route('/albums/<album_id>/tracks', methods=['POST'])
def create_cancion_database(album_id):

    print(request.is_json)
    data = request.get_json()
    key = data.keys()
    k = Album.query.get(album_id)
    if k == None:
        data = 'álbum no existe'
        return json.dumps(data, ensure_ascii=False), 422

    llaves = []
    for i in key:
        llaves.append(i)
    key0 = llaves[0]
    key1 = llaves[1]
    if key0 != 'name' or key1 != 'duration':
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400

    if type(data['name']) != str or type(data['duration'])!= float:
        data = 'input inválido'
        return json.dumps(data, ensure_ascii=False), 400

    name = data['name']
    duration = data['duration']
    print(name, duration)

    times_played = 0
    #codificar
    codi = name + ':' + album_id
    encoded_name = b64encode(codi.encode()).decode('utf-8')
    encoded_name = cut_codification(encoded_name)
    #get id artista
    buscar_album_id = Album.query.get(album_id)
    artist_id = buscar_album_id.artist_id
    print(artist_id)
    artist_id = Artista.query.get(artist_id)
    print(artist_id)
    path_artist = '/artists/'+ artist_id.id
    path_album = '/artists/'+ album_id 
    path_self = '/albums/'+ album_id + '/tracks'
    try:
        track = Cancion(id= encoded_name, album_id = album_id, name = name, duration = duration, times_played = times_played, artist = path_artist, album = path_album, self_url = path_self)  
        db.session.add(track)
        db.session.commit()
        data = 'canción creada'

    except IntegrityError:
        db.session.rollback()
        i = Cancion.query.get(encoded_name)
        print('Existe')
        dicc={'id' : i.id, 'album_id': i.album_id, 'name': i.name, 'duration' : i.duration, 'artist' : i.artist, 'album': i.album, 'self': i.self_url}
        return json.dumps(dicc, ensure_ascii=False), 409
    except DataError:
        print("data")
    except KeyError:
        print("data")
    
    return json.dumps(data, ensure_ascii=False), 201


@app.route('/artists/<artist_id>/tracks', methods=['GET'])
def obtener_artis_track(artist_id):
    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista no encontrado'
        return json.dumps(data, ensure_ascii=False), 422
    else:
        lista_albumes = Album.query.filter_by(artist_id=artist_id).all()
        tracks = []
        for i in lista_albumes:
            album = Album.query.get(i.id)
            lista_tracks_album = Cancion.query.filter_by(album_id=album.id).all()
            for i in lista_tracks_album:
                dicc={'id' : i.id, 'album_id': i.album_id, 'name': i.name, 'duration' : i.duration, 'artist' : i.artist, 'album': i.album, 'self': i.self_url}
                tracks.append(dicc)
                print('nombre :', i.name)    
        return json.dumps(tracks, ensure_ascii=False), 200

@app.route('/tracks', methods=['GET'])
def get_tracks():
    all_tracks = Cancion.query.all()
    print(all_tracks)
    all = []
    for i in all_tracks:
        #j = jsonify(id = i.id, name=i.name, genre= i.genre, artist= i.artist, tracks=i.tracks, self = i.self_url)  
        dicc={'id' : i.id, 'album_id': i.album_id, 'name': i.name, 'duration' : i.duration, 'artist' : i.artist, 'album': i.album, 'self': i.self_url}
        all.append(dicc)
    print(all)
    print("aca", json.dumps(all))
    return json.dumps(all, ensure_ascii=False), 200


@app.route('/artists/<artist_id>/albums/play', methods=['PUT'])
def play_artist_albums_tracks(artist_id):

    k = Artista.query.get(artist_id)
    if k == None:
        data = 'artista no encontrado'
        return json.dumps(data, ensure_ascii=False), 404

    lista_albumes = Album.query.filter_by(artist_id=artist_id).all()
    tracks = []
    for i in lista_albumes:
        album = Album.query.get(i.id)
        print('nombre album: ', album.name)
        lista_tracks_album = Cancion.query.filter_by(album_id=album.id).all()
        for i in lista_tracks_album:
            print('before: ', i.times_played)
            num = i.times_played
            i.times_played = num + 1
            print('after: ', i.times_played)
            db.session.commit() 
    data = 'todas las canciones del artista fueron reproducidas'
    return json.dumps(data, ensure_ascii=False), 200


@app.route('/albums/<album_id>/tracks/play', methods=['PUT'])
def play_album_tracks(album_id):
    k = Album.query.get(album_id)
    if k == None:
        data = 'álbum no encontrado'
        return json.dumps(data, ensure_ascii=False), 404
    
    album = Album.query.get(album_id)    
    buscar_track = Cancion.query.filter_by(album_id=album_id).all()
    for i in buscar_track:
        print('before: ', i.times_played)
        num = i.times_played
        i.times_played = num + 1
        print('after: ', i.times_played)
        db.session.commit()
    data = 'canciones del álbum reproducidas'
    return json.dumps(data, ensure_ascii=False), 200

@app.route('/tracks/<track_id>/play', methods=['PUT'])
def play_track(track_id):
    k = Cancion.query.get(track_id)
    if k == None:
        data = 'canción no encontrada'
        return json.dumps(data, ensure_ascii=False), 404

    track = Cancion.query.get(track_id)
    num = track.times_played
    track.times_played = num + 1
    db.session.commit()
    data = 'canción reproducida'
    return json.dumps(data, ensure_ascii=False), 200

@app.route('/tracks/<track_id>', methods=['DELETE'])
def delete_track(track_id):
    k = Cancion.query.get(track_id)
    if k == None:
        data = 'canción inexistente'
        return json.dumps(data, ensure_ascii=False), 404
    data = 'canción eliminada'
    track = Cancion.query.get(track_id)
    db.session.delete(track)
    db.session.commit()
    data = 'canción eliminada'
    return json.dumps(data, ensure_ascii=False), 200

@app.route('/tracks/<track_id>', methods=['GET'])
def obtener_track(track_id):
    k = Cancion.query.get(track_id)
    if k == None:
        data = 'Canción no encontradae'
        return json.dumps(data, ensure_ascii=False), 404


    i = Cancion.query.get(track_id)
    dicc={'id' : i.id, 'album_id': i.album_id, 'name': i.name, 'duration' : i.duration, 'artist' : i.artist, 'album': i.album, 'self': i.self_url}
    return json.dumps(dicc, ensure_ascii=False), 200

###################################################################
if __name__ == "__main__":
    app.run(debug=True)
    