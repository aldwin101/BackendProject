from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app
import datetime



@app.route("/api/comments", methods = ["GET", "POST", "PATCH", "DELETE"])
    # comment handler
def comments():
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
                cursor.execute("SELECT comment.id, tweet_id, user_id, username, content, created_at FROM user INNER JOIN comment ON user.id=comment.user_id WHERE user_id=?", [userId])
                getUserComment = cursor.fetchall()
                print(getUserComment)

                if getUserComment != None:
                    getAllUserComments = []
                    for comment in getUserComment:
                        userComments = {
                            "commentId" : comment[0],
                            "tweetId" : comment[1],
                            "userId" : comment[2],
                            "username" : comment[3],
                            "content" : comment[4],
                            "createdAt" : comment[5]
                        }
                        getAllUserComments.append(userComments)
            
                return Response(json.dumps(getAllUserComments, default=str),
                                mimetype="application/json",
                                status=200)

            else:
                cursor.execute("SELECT comment.id, tweet_id, user_id, username, content, created_at FROM user INNER JOIN comment ON user.id=comment.user_id")
                allComments = cursor.fetchall()
                
                if allComments != None:
                    allCommentsData = []
                    for comment in allComments:
                        userComment = {
                            "commentId" : comment[0],
                            "tweetId" : comment[1],
                            "userId" : comment[2],
                            "username" : comment[3],
                            "content" : comment[4],
                            "createdAt" : comment[5]
                        }
                        allCommentsData.append(userComment) 

                    return Response(json.dumps(allCommentsData, default=str),
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
            commentId= cursor.fetchone()[0]
            print(commentId)

            if userId != None and commentId != None:
                cursor.execute("INSERT INTO comment(tweet_id, user_id, content, created_at) VALUES (?,?,?,?)", [commentId, userId, data.get('content'), datetime.datetime.today()])
                conn.commit()
                getCommentId = cursor.lastrowid
                print(getCommentId)

                cursor.execute("SELECT comment.id, tweet_id, user_id, username, content, created_at FROM user INNER JOIN comment ON user.id=comment.user_id WHERE comment.id=?", [getCommentId])
                getUserComment = cursor.fetchone()
                print(getUserComment)

                newUserComment= {
                    "commentId" : getUserComment[0],
                    "tweetId" : getUserComment[1],
                    "userId": getUserComment[2],
                    "username" : getUserComment[3],
                    "content" : getUserComment[4],
                    "createdAt" : getUserComment[5],
                }

                return Response(json.dumps(newUserComment, default=str),
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

            cursor.execute("SELECT id FROM comment WHERE id=?",[data.get("commentId")])
            commentId= cursor.fetchone()[0]
            print(commentId)

            if sessionUserId != None and commentId != None:
                if data.get("content") != "" and data.get("content") != None:
                    cursor.execute("UPDATE comment SET content = ? WHERE id = ?", [data.get("content"), commentId])

                else:
                    return Response("field cannot be empty", 
                                    mimetype="text/html", 
                                    status=400)
                conn.commit()

                cursor.execute("SELECT comment.id, tweet_id, user_id, username, content, created_at FROM user INNER JOIN comment ON user.id=comment.user_id WHERE comment.id=?", [commentId])
                getUpdatedComment = cursor.fetchone()
                print (getUpdatedComment)

                updatedComment = {
                    "commentId" : getUpdatedComment[0],
                    "tweetId" : getUpdatedComment[1],
                    "userId" : getUpdatedComment[2],
                    "username" : getUpdatedComment[3],
                    "content" : getUpdatedComment[4],
                    "createdAt" : getUpdatedComment[5]
                }

                return Response(json.dumps(updatedComment, default=str), 
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

            cursor.execute("SELECT id FROM comment WHERE id=?",[data.get("commentId")])
            commentId= cursor.fetchone()[0]
            print(commentId)
            

            if sessionUserId != None and commentId != None:
                cursor.execute('DELETE FROM comment WHERE id=?',[commentId])
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