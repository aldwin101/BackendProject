from os import path
import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app



@app.route("/api/comment-likes", methods = ["GET", "POST", "DELETE"])
    # comment like handler
def commentLikes():
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
            cursor.execute("SELECT comment_id, user_id, username FROM user INNER JOIN comment_like ON user.id=comment_like.user_id")
            getAllCommentLikes = cursor.fetchall()
            
            if getAllCommentLikes != None:
                allCommentLikes = []
                for like in getAllCommentLikes:
                    commentLike = {
                        "commentId" : like[0],
                        "userId" : like[1],
                        "username" : like[2]
                    }
                    allCommentLikes.append(commentLike) 

                return Response(json.dumps(allCommentLikes, default=str),
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

            cursor.execute("SELECT id FROM comment WHERE id=?",[data.get("commentId")])
            commentId= cursor.fetchone()[0]
            print(commentId)

            if userId != None and commentId != None:
                cursor.execute("INSERT INTO comment_like(comment_id, user_id) VALUES (?,?)", [commentId, userId])
                conn.commit()
                cursor.execute("SELECT comment_id, user_id, username FROM user INNER JOIN comment_like ON user.id=comment_like.user_id WHERE comment_id=?",[commentId])
                getLikeComment = cursor.fetchone()
                print(getLikeComment)

                likeComment = {
                    "commentId" : getLikeComment[0],
                    "userId" : getLikeComment[1],
                    "username": getLikeComment[2]
                }

                return Response(json.dumps(likeComment, default=str),
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

            cursor.execute("SELECT id FROM comment WHERE id=?",[data.get("commentId")])
            reqDelCommentId= cursor.fetchone()[0]
            print(reqDelCommentId)
            
            if reqDelUserId != None and reqDelCommentId != None:
                cursor.execute('DELETE FROM comment_like WHERE user_id=? and comment_id=?',[reqDelUserId, reqDelCommentId])
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