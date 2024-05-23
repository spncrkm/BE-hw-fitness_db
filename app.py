from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    credit_card = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "credit_card", "member_id")


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

db_name = "fitness_db"
user = "root"
password = "Emilyalice1001"
host = "localhost"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        if conn.is_connected():
            print("Connected to db successfully")
            return conn
        
    except Error as e:
        print(f"Error: {e}")
        return None
    
@app.route("/")

def home():
    return "Hello there! Thanks for coming to our fitness center!"


@app.route("/members", methods=["POST"])
def add_member():

    member_data = member_schema.load(request.json)
    print(member_data)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    name = member_data['name']
    email = member_data['email']
    phone = member_data['phone']
    credit_card = member_data['credit_card']

    new_member = (name, email, phone, credit_card)
    print(new_member)

    query = "INSERT INTO Orders(name, email, phone, credit_card) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, new_member)
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"message": "New member was added successfully"}), 201


@app.route("/members/<int:id>", methods = ["GET"])
def get_members():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Members"
    cursor.execute(query)

    members = cursor.fetchall()
    print(members)

    cursor.close()
    conn.close()

    return members_schema.jsonify(members)


class WorkoutSchema(ma.Schema):
    member_id = fields.Int(required=True)
    time = fields.Time(required=True)
    date = fields.Date(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("member_id", "time", "date", "activity")

workout_schema = MemberSchema()
workouts_schema = MemberSchema(many=True)

@app.route("/schedule", methods = ["POST"])
def add_workout():
    member_data = workout_schema.load(request.json)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    date = member_data["date"]
    time = member_data["time"]
    activity = member_data["activity"]
    member_id = member_data["member_id"]

    new_workout = (activity, date, time, member_id)

    query = "INSERT INTO Workouts(activity, date, time, member_id)"

    cursor.execute(query, new_workout)
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "New workout was added successfully"}), 201

@app.route("/members/schedule", methods = ["GET"])
def get_workout():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Workouts"
    cursor.execute(query)
    workouts = cursor.fetchall()
    print(workouts)

    cursor.close()
    conn.close()
    return members_schema.jsonify(workouts)

@app.route("/members/schedule/<int:member_id>", methods = ["PUT"])
def update_workout(member_id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": f"{err.messages}"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database Connection Failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Workouts SET date = %s, time = %s, activity = %s WHERE member_id = %s"
        date = member_data["date"]
        time = member_data["time"]
        member_id = member_data["member_id"]
        activity = member_data["activity"]
        updated_workout = (date, time, activity, member_id)
        cursor.execute(query, updated_workout)
        conn.commit()
        return jsonify({'message': "Workout was updated successfully"}), 200
    
    except Error as e:
        return jsonify({"error": f"{e}"}), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route("/members/schedule/<int:member_id>", methods=["DELETE"])
def delete_workout(member_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Workouts WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        conn.commit()
        return jsonify({"message": "Workout successfully deleted!"}), 200
    
    except Error as e:
        return jsonify({"error": f"{e}"}), 500
    
    finally:
        cursor.close()
        conn.close()
        


if __name__ == "__main__":
    app.run(debug=True)