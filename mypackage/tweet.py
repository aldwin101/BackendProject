from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app
import datetime



@app.route("/api/tweets", methods = ["GET", "POST", "PATCH", "DELETE"])
    # tweet handler
def tweets():
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
            params = request.args.get("userId")
            if params != "" and params != None:
                cursor.execute("SELECT id FROM user WHERE id=?",[params])
                userId = cursor.fetchone()[0]
                print(userId)
                cursor.execute("SELECT tweet.id, user_id, username, content, created_at, user_image_url, tweet_image_url FROM user INNER JOIN tweet ON user.id=tweet.user_id WHERE user_id=?", [userId])
                getUserTweet = cursor.fetchall()
                print(getUserTweet)

                if getUserTweet != None:
                    getAllUserTweets = []
                    for comment in getUserTweet:
                        userTweets = {
                            "commentId" : comment[0],
                            "tweetId" : comment[1],
                            "userId" : comment[2],
                            "username" : comment[3],
                            "content" : comment[4],
                            "createdAt" : comment[5]
                        }
                        getAllUserTweets.append(userTweets)
            
                return Response(json.dumps(getAllUserTweets, default=str),
                                mimetype="application/json",
                                status=200)

            else:
                cursor.execute("SELECT tweet.id, user_id, username, content, created_at, user_image_url, tweet_image_url FROM user INNER JOIN tweet ON user.id=tweet.user_id")
                allTweets = cursor.fetchall()
                print(allTweets)
                
                if allTweets != None:
                    allTweetsData = []
                    for tweet in allTweets:
                        userTweet = {
                            "tweetId" : tweet[0],
                            "userId" : tweet[1],
                            "username" : tweet[2],
                            "content" : tweet[3],
                            "createdAt" : tweet[4],
                            "userImageUrl" : tweet[5],
                            "tweetImageUrl" : tweet[6]
                        }
                        allTweetsData.append(userTweet) 

                    return Response(json.dumps(allTweetsData, default=str),
                                    mimetype="application/json",
                                    status=200)

                else:
                    return Response("Wrong data",
                                    mimetype='text/html',
                                    status=400)
        
                # POST
        elif request.method == "POST":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[data.get('loginToken')])
            userId = cursor.fetchone()[0]

            if userId != None:
                cursor.execute("INSERT INTO tweet(user_id, content, tweet_image_url, created_at) VALUES (?,?,?,?)", [userId, data.get('content'), data.get('imageUrl'), datetime.datetime.today()])
                conn.commit()
                getTweetId = cursor.lastrowid

                cursor.execute("SELECT tweet.id, user_id, username, content, created_at, user_image_url, tweet_image_url FROM user INNER JOIN tweet ON user.id=tweet.user_id WHERE tweet.id=?", [getTweetId])
                getUserTweetData = cursor.fetchone()

                newUserTweetData= {
                    "tweetId" : getUserTweetData[0],
                    "userId" : getUserTweetData[1],
                    "username": getUserTweetData[2],
                    "content" : getUserTweetData[3],
                    "createdAt" : getUserTweetData[4],
                    "userImageUrl" : getUserTweetData[5],
                    "imageUrl" : getUserTweetData[6],
                }

                return Response(json.dumps(newUserTweetData, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                return Response("Fiil out the required information",
                                mimetype="text/html",
                                status=400)

                # PATCH
        elif request.method == "PATCH":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [data.get("loginToken")])
            sessionUserId = cursor.fetchone()[0]
            print(sessionUserId)

            cursor.execute("SELECT id FROM tweet WHERE id=?",[data.get("tweetId")])
            tweetId= cursor.fetchone()[0]
            print(tweetId)

            if sessionUserId != None and tweetId != None:
                if data.get("content") != "" and data.get("content") != None:
                    cursor.execute("UPDATE tweet SET content = ? WHERE id = ?", [data.get("content"), tweetId])
                    cursor.execute("UPDATE tweet SET tweet_image_url = ? WHERE id = ?", [data.get("imageUrl"), tweetId])

                else:
                    return Response("field cannot be empty", 
                                    mimetype="text/html", 
                                    status=400)
                conn.commit()

                cursor.execute("SELECT id, content FROM tweet WHERE id=?", [tweetId])
                getUpdatedTweet = cursor.fetchone()
                print (getUpdatedTweet)

                updatedTweet = {
                    "tweetId": getUpdatedTweet[0],
                    "content": getUpdatedTweet[1]
                }

                return Response(json.dumps(updatedTweet, default=str), 
                                mimetype="application/json", 
                                status=200)
            else:
                return Response("Value cannot be None", 
                                mimetype="text/html", 
                                status=400)

                # DELETE
        elif request.method == "DELETE":
            data = request.json
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [data.get("loginToken")])
            sessionUserId = cursor.fetchone()[0]
            print(sessionUserId)

            cursor.execute("SELECT id FROM tweet WHERE id=?",[data.get("tweetId")])
            tweetId= cursor.fetchone()[0]
            print(tweetId)
            
            if sessionUserId != None and tweetId != None:
                cursor.execute("DELETE FROM tweet WHERE id=?",[tweetId])
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