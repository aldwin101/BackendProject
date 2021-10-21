from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app

@app.route("/api/followers", methods = ["GET"])
    # follower handler
def followers():
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
                cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user INNER JOIN follow ON user.id=follow.follower WHERE user_id=?",[userId])
                getFollowerData = cursor.fetchall()
                print(getFollowerData)

                allFollowerData = []

                for followerData in getFollowerData:
                    followerUserData = {
                        "userId" : followerData[0],
                        "email" : followerData[1],
                        "username" : followerData[2],
                        "bio" : followerData[3],
                        "birthdate" : followerData[4],
                        "imageUrl" : followerData[5],
                        "bannerUrl" : followerData[6],
                    }
                    allFollowerData.append(followerUserData)
                
                return Response(json.dumps(allFollowerData, default=str),
                                mimetype="application/json",
                                status=200)

            else:
                return Response("Invalid id",
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
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")