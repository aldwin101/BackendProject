from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app



@app.route("/api/tweet-likes", methods = ["GET", "POST", "DELETE"])
    # tweet like handler
def tweetLikes():
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
            cursor.execute("SELECT tweet_id, user_id, username FROM user INNER JOIN tweet_like ON user.id=tweet_like.user_id")
            getAllTweetLikes = cursor.fetchall()
            
            if getAllTweetLikes != None:
                allTweetLikes = []
                for like in getAllTweetLikes:
                    tweetLike = {
                        "tweetId" : like[0],
                        "userId" : like[1],
                        "username" : like[2]
                    }
                    allTweetLikes.append(tweetLike) 

                return Response(json.dumps(allTweetLikes, default=str),
                                mimetype="application/json",
                                status=200)

            else:
                return Response("Wrong data",
                                mimetype='text/html',
                                status=400)
        
                # POST
        elif request.method == "POST":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]
            print(userId)

            cursor.execute("SELECT id FROM tweet WHERE id=?",[data.get("tweetId")])
            tweetId= cursor.fetchone()[0]
            print(tweetId)

            if userId != None and tweetId != None:
                cursor.execute("INSERT INTO tweet_like(tweet_id, user_id) VALUES (?,?)", [tweetId, userId])
                conn.commit()
                cursor.execute("SELECT tweet_id, user_id, username FROM user INNER JOIN tweet_like ON user.id=tweet_like.user_id WHERE tweet_id=?",[tweetId])
                getLikeData = cursor.fetchone()
                print(getLikeData)

                likeData = {
                    "tweetId" : getLikeData[0],
                    "userId" : getLikeData[1],
                    "username": getLikeData[2]
                }

                return Response(json.dumps(likeData, default=str),
                                mimetype="application/json",
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

            cursor.execute("SELECT id FROM tweet WHERE id=?",[data.get("tweetId")])
            reqDelTweetId= cursor.fetchone()[0]
            print(reqDelTweetId)
            
            if reqDelUserId != None and reqDelTweetId != None:
                cursor.execute('DELETE FROM tweet_like WHERE user_id=? and tweet_id=?',[reqDelUserId, reqDelTweetId])
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