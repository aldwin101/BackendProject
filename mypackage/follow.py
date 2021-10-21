from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app

@app.route("/api/follows", methods = ["GET", "POST", "DELETE"])
    # follow handler
def follows():
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
            params = request.args
            cursor.execute("SELECT id FROM user WHERE id=?",[params.get("userId")])
            userId = cursor.fetchone()[0]
            print(userId)

            if userId != None:
                cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user INNER JOIN follow ON user.id=follow.followed WHERE user_id=?",[userId])
                getFollowedData = cursor.fetchall()
                print(getFollowedData)

                allFollowedData = []

                for followedData in getFollowedData:
                    followedUserData = {
                        "userId" : followedData[0],
                        "email" : followedData[1],
                        "username" : followedData[2],
                        "bio" : followedData[3],
                        "birthdate" : followedData[4],
                        "imageUrl" : followedData[5],
                        "bannerUrl" : followedData[6],
                    }
                    allFollowedData.append(followedUserData)
                
                return Response(json.dumps(allFollowedData, default=str),
                                mimetype="application/json",
                                status=200)

            else:
                return Response("Invalid id",
                                mimetype='text/html',
                                status=400)
                
                # POST
        elif request.method == "POST":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [data.get("loginToken")])
            sessionUserId = cursor.fetchone()[0]
            print(sessionUserId)

            cursor.execute("SELECT id FROM user WHERE id=?",[data.get("followId")])
            followId= cursor.fetchone()[0]
            print(followId)

            if sessionUserId != None and followId != None:
                cursor.execute("INSERT INTO follow(followed, user_id) VALUES (?,?)", [followId, sessionUserId])
                conn.commit()

                return Response("followed",
                                mimetype="text/html",
                                status=200)
            else:
                return Response("Invalid data sent",
                                mimetype="text/html",
                                status=400)

                # DELETE
        elif request.method == "DELETE":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [data.get("loginToken")])
            reqDelUserId = cursor.fetchone()[0]
            print(reqDelUserId)

            cursor.execute("SELECT followed FROM follow WHERE followed=?",[data.get("followId")])
            reqDelfollowedId= cursor.fetchone()[0]
            print(reqDelfollowedId)
            
            if reqDelUserId != None and reqDelfollowedId != None:
                cursor.execute('DELETE FROM follow WHERE user_id=? and followed=?',[reqDelUserId, reqDelfollowedId])
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
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")