from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app


@app.route("/api/users", methods = ["GET", "POST", "PATCH", "DELETE"])
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
        if request.method == "GET":
            cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user")
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
                                mimetype="application/json",
                                status=200)

            else:
                return Response("Wrong data",
                                mimetype='text/html',
                                status=400)
        
                # POST
        elif request.method == "POST":
            data = request.json
            generateLoginToken = uuid.uuid4().hex

            cursor.execute("INSERT INTO user (email, username, password, bio, birthdate, image_url, banner_url) VALUES (?,?,?,?,?,?,?) ",
                [data.get("email"), data.get("username"), data.get("password"), data.get("bio"), data.get("birthdate"), data.get("imageUrl"), data.get("bannerUrl")])
            conn.commit()
            getNewUserId = cursor.lastrowid

            cursor.execute("SELECT * FROM user WHERE id=?", [getNewUserId])
            getNewUserData = cursor.fetchone()

            newUserData= {
                "userId" : getNewUserData[0],
                "email" : getNewUserData[1],
                "username": getNewUserData[2],
                "bio" : getNewUserData[3],
                "birthdate" : getNewUserData[4],
                "imageUrl" : getNewUserData[5],
                "bannerUrl" : getNewUserData[6],
            }

            if generateLoginToken != None:
                return Response(json.dumps(newUserData, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                return Response("Fiil out the required information",
                                mimetype="text/html",
                                status=400)

                # PATCH
        elif request.method == "PATCH":
            data = request.json
            
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]

            if userId != None:
                    # allow you to edit single data
                if data.get("email") != "" and data.get("email") != None:
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [data.get("email"), userId])

                elif data.get("username") != "" and data.get("username") != None:
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [data.get("username"), userId])

                elif data.get("password") != "" and data.get('password') != None:
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [data.get('password'), userId])

                elif data.get("bio") != "" and data.get("bio") != None:
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [data.get("bio"), userId])

                elif data.get("birthdate") != "" and data.get("birthdate") != None:
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [data.get("birthdate"), userId])

                elif data.get("imageUrl") != "" and data.get("imageUrl") != None:
                    cursor.execute("UPDATE user SET imageUrl = ? WHERE id = ?", [data.get("imageUrl"), userId])

                elif data.get("bannerUrl") != "" and data.get("bannerUrl") != None:
                    cursor.execute("UPDATE user SET imageUrl = ? WHERE id = ?", [data.get("bannerUrl"), userId])

                else: 
                    return Response("field cannot be empty", 
                                    mimetype="text/html", 
                                    status=400)
                conn.commit()

                cursor.execute("SELECT * FROM user WHERE id=?", [userId])
                getUpdatedUserData = cursor.fetchone()

                updatedUserData = {
                    "userId": getUpdatedUserData[0],
                    "email": getUpdatedUserData[1],
                    "username": getUpdatedUserData[2],
                    "bio": getUpdatedUserData[3],
                    "birthdate": getUpdatedUserData[4],
                    "imageUrl": getUpdatedUserData[5],
                    "bannerUrl": getUpdatedUserData[6]
                }

                return Response(json.dumps(updatedUserData, default=str), 
                                mimetype="application/json", 
                                status=200)
            else:
                return Response("Value cannot be None", 
                                mimetype="text/html", 
                                status=400)

                # DELETE
        elif request.method == "DELETE":
            data = request.json
            getPassword = data.get("password")
            getLoginToken = data.get("loginToken")

            if getPassword != None and getLoginToken != None:
                cursor.execute("DELETE user, user_session FROM user INNER JOIN user_session ON user.id=user_session.user_id WHERE password=? and login_token=?",[getPassword, getLoginToken])
                conn.commit()

                return Response("Deleted successfully", 
                                mimetype="text/html", 
                                status=200)
            else:
                return Response("Delete Failed", 
                                mimetype="text/html", 
                                status=400) 

        else:
            return Response("Invalid call",
                            mimetype="text/html",
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