from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from dotenv import load_dotenv
import os 
load_dotenv()


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
secret = os.getenv("JWT_SECRET_KEY")
if not secret:
    raise RuntimeError("JWT_SECRET_KEY missing – set it in .env")
app.config["JWT_SECRET_KEY"] = secret

db = SQLAlchemy(app)
jwt = JWTManager(app)

# miodel
class User(db.Model):
    id  = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80),unique = True,nullable=True)
    password  = db.Column(db.String(120),nullable =False)
with app.app_context():
    db.create_all()
#register
@app.route("/register",methods = ["POST"])
def register():
    data = request.json
    if User.query.filter_by(username = data["username"]).first():
        return jsonify({"msg":"user exists already exists"}),400
    new_user = User(username=data["username"],password = data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg":"User created successfully"}),201
#login
@app.route("/login",methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username = data["username"],password = data["password"]).first()
    if not user:
        return jsonify({"msg":"Invalid credentials"}),401
    token = create_access_token(identity =user.id)
    return jsonify(access_token = token)
# get profile 
@app.route("/profile",methods = ["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(id = user.id,username = user.username)
# update profile 
@app.route("/profile",methods = ["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.json
    user.username = data.get('username',user.username)
    db.session.commit()
    return jsonify({"msg":"Profile updated"})
#Delete Profile
@app.route("/profile",methods = ["DELETE"])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg":"User Deleted"})
#Sign out (handled client-side by deleting token )
@app.route("/logout",methods = ["POST"])
@jwt_required()
def logout():
    return jsonify({"msg":"Logout successful -  just delete token on client"})
if __name__ == "__main__":
    app.run(debug=True)