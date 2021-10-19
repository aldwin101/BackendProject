import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app

@app.route('/api/login', methods=['POST', 'DELETE'])

def login():
    try:
        cursor = None
        conn = None

        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port, 
                        database=dbcreds.database
                        )
        cursor = conn.cursor()
            #login user
        if request.method == 'POST':
            data = request.json
            cursor.execute('SELECT email, password FROM user WHERE email=? and password = ?',[data.get('email'), data.get('password')])
            getloginData = cursor.fetchone()
            email = getloginData[0]
            password = getloginData[1]

            if email != None and password != None:
                generateToken = uuid.uuid4().hex
                cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?,(SELECT id FROM user WHERE email=?));", [generateToken, data.get('email')])
                conn.commit()

                cursor.execute('SELECT user.id, email, username, bio, birthdate, image_url, banner_url, login_token FROM user INNER JOIN user_session ON user.id=user_session.user_id WHERE email=? AND password=?',
                                [email, password])
                info = cursor.fetchone()
            
                resp = {
                    'id' : info[0],
                    'email' : info[1],
                    'username' : info[2],
                    'bio' : info[3],
                    'birthdate' : info[4],
                    'imageUrl' : info[5],
                    'bannerUrl' : info[6],
                    'loginToken' : info[7]
                }
                return Response(json.dumps(resp, default=str),
                                mimetype='application/json',
                                status=200)
            else:
                return Response('Invalid email or password',
                                mimetype='text/html',
                                status=400)


        elif request.method == 'DELETE':
            data = request.json
            getLoginToken = data.get('loginToken')
            print(getLoginToken)

            if getLoginToken != None:
                cursor.execute('DELETE FROM user_session where login_token=?',[getLoginToken])
                conn.commit()

                return Response("Logged Out",
                            mimetype='text/html',
                                status=200)

            else:
                return Response("Invalid token",
                                mimetype='text/html',
                                status=400)
        else:
            return Response("Invalid method",
                                mimetype='text/html',
                                status=500)

    except mariadb.OperationalError:
        print("Operational error on the query")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.OperationalError:
        print("Something wrong with the connection")
    except mariadb.ProgrammingError:
        print("Your query was wrong")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    except:
        print("Something went wrong")
    finally:
        if (cursor != None):
            cursor.close()
        else:
            print("There was never a cursor to begin with")
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")


