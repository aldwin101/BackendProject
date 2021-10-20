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