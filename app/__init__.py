from flask import Flask

app = Flask(__name__)

import mypackage.users
import mypackage.login
import mypackage.tweet
import mypackage.comments
import mypackage.tweetLike
import mypackage.commentLike
import mypackage.follow