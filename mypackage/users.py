from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app


          # ******************** user endpoint ********************
@app.route('/api/users', methods = ['GET', 'POST', 'PATCH', 'DELETE'])
    # users handler
def users():
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
                # GET
        if request.method == 'GET':
            cursor.execute('SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user')
            allUsers = cursor.fetchall()
            
            if allUsers != None:
                allUsersData = []
                for user in allUsers:
                    userData = {
                        "userId" : user[0],
                        "email" : user[1],
                        "username" : user[2],
                        "bio" : user[3],
                        "birthdate" : user[4],
                        "imageUrl" : user[5],
                        "bannerUrl" : user[6]
                    }
                    allUsersData.append(userData)

                return Response(json.dumps(allUsersData, default=str),
                                mimetype='application/json',
                                    status=200)

            else:
                return Response("Wrong data",
                                mimetype='text/html',
                                    status=400)
        
                # POST
        elif request.method == 'POST':
            data = request.json
            generateLoginToken = uuid.uuid4().hex
            cursor.execute('INSERT INTO user (email, username, password, bio, birthdate, image_url, banner_url) VALUES (?,?,?,?,?,?,?)',
                [data.get('email'), data.get('username'), data.get('password'), data.get('bio'), data.get('birthdate'), data.get('image_url'), data.get('banner_url')])
            conn.commit()

            newUserData= {
                'email' : data.get('email'),
                'username' : data.get('username'),
                'bio' : data.get('bio'),
                'birthdate' : data.get('birthdate'),
                'imageUrl' : data.get('image_url'),
                'bannerUrl' : data.get('banner_url'),
                'loginToken' : generateLoginToken
            }

            if generateLoginToken != None:
                return Response(json.dumps(newUserData),
                                mimetype='application/json',
                                status=200)
            else:
                return Response("Fiil out the required information",
                                mimetype='text/html',
                                status=400)

                # PATCH
        elif request.method == 'PATCH':
            data = request.json
            patchReqLoginToken = data.get('loginToken')
            print(patchReqLoginToken)

            if patchReqLoginToken != None:
                cursor.execute("UPDATE user INNER JOIN user_session ON user.id=user_session.user_id SET email=?, username=?, password=?, bio=?, birthdate=?, image_url=?, banner_url=? WHERE login_token=?", 
                                [data.get('email'), data.get('username'), data.get('bio'), data.get('birthdate'), data.get('image_url'), data.get('banner_url'), patchReqLoginToken])
                conn.commit()
                updateUserData = cursor.fetchone()
                print(updateUserData)

                updatedData = {
                    'userId': data.get('id'),
                }
                return Response(json.dumps(updatedData), 
                                mimetype="application/json", 
                                status=200)
            else:
                return Response("Please fillout the important data", 
                                mimetype="text/html", 
                                status=500)


                # DELETE
        elif request.method == 'DELETE':
            data = request.json
            getReqPassword = data.get('password')
            getReqLoginToken = data.get('loginToken')

            if getReqPassword != None and getReqLoginToken != None:
                cursor.execute('DELETE user, user_session FROM user INNER JOIN user_session ON user.id=user_session.user_id WHERE password=? and login_token=?',[getReqPassword, getReqLoginToken])
                conn.commit()

                return Response("Successfully deleted", mimetype="text/html", status=200)
            else:
                return Response("Delete Failed", mimetype="text/html", status=400) 

        else:
            return Response(json.dumps('Invalid call'),
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
        # Check the connection
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")