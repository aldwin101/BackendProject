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
def users_handler():
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
                return Response("Invalid Call",
                                mimetype='text/html',
                                    status=400)
        
                # POST
        elif request.method == 'POST':
            data = request.json
            generateToken = uuid.uuid4().hex
            cursor.execute('INSERT INTO user (email, username, password, bio, birthdate, image_url, banner_url) VALUES (?,?,?,?,?,?,?)',
                [data.get('email'), data.get('username'), data.get('password'), data.get('bio'), data.get('birthdate'), data.get('image_url'), data.get('banner_url')])
            conn.commit()


            resp = {
                'email' : data.get('email'),
                'username' : data.get('username'),
                'bio' : data.get('bio'),
                'birthdate' : data.get('birthdate'),
                'imageUrl' : data.get('image_url'),
                'bannerUrl' : data.get('banner_url'),
                'loginToken' : generateToken
            }

            if generateToken != None:
                return Response(json.dumps(resp),
                                mimetype='application/json',
                                status=200)
            else:
                return Response("Fiil out the required information",
                                mimetype='text/html',
                                status=400)

                # PATCH
        elif request.method == 'PATCH':
            data = request.json
            username = request.json.get("username") 
            bio = request.json.get("bio")
            birthdate = request.json.get("birthdate")
            email = request.json.get("email")
            loginToken =request.json.get("loginToken")
            rows = None
            cursor.execute("SELECT login_token FROM user_session WHERE login_token = ?", [loginToken])
            user_id= cursor.fetchone()[0]
            print(user_id)
            if username != "" and username != None:
                cursor.execute("UPDATE user SET username=? WHERE id=?", [username, user_id])
            if email != "" and email != None:
                cursor.execute("UPDATE user SET email=? WHERE id=?", [email, user_id])
            if bio != "" and bio != None:
                cursor.execute("UPDATE user SET bio=? WHERE id=?", [bio, user_id])
            if birthdate != "" and birthdate != None:
                cursor.execute("UPDATE user SET birthdate=? WHERE id=?", [birthdate, user_id])
            conn.commit() 
            rows = cursor.rowcount 
            cursor.execute("SELECT * FROM user WHERE id = ?", [user_id])
            user = cursor.fetchone()
                
            if (rows == 1):
                print(user)
                userData = {
                    "userId":user[0],
                    "username":user[1], 
                    "email":user[2], 
                    "bio":user[3], 
                    "birthdate":user[4]
                    }
                return Response(json.dumps(userData), 
                                mimetype="application/json", 
                                status=200)
            else:
                return Response("Please fillout the important data", 
                                mimetype="text/html", 
                                status=500)


                # DELETE
        elif request.method == 'DELETE':
            rows = None
            data = request.json
            loginToken = request.json.get("loginToken")
            password = request.json.get("password")
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
            user_id= cursor.fetchone()[0]
            cursor.execute("DELETE FROM user WHERE id=? AND password= ?", [user_id, password])
            conn.commit() 
            rows = cursor.rowcount 
            if (rows == 1):
                return Response("Delete Success", mimetype="text/html", status=204)
            else:
                return Response("Delete Failed", mimetype="text/html", status=500) 

        else:
            return Response(json.dumps('Invalid call'),
                                mimetype='text/html',
                                status=400)

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