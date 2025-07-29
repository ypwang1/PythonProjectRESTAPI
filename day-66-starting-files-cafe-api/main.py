from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    cafe = random.choice(all_cafes)
    print(all_cafes)
    return jsonify(cafe={
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
    })

@app.route("/all")
def all_cafes():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    cafe_list = []
    for each_cafe in cafes:
        cafe_list.append({
            "id": each_cafe.id,
            "name": each_cafe.name,
            "map_url": each_cafe.map_url,
            "img_url": each_cafe.img_url,
            "location": each_cafe.location,
            "seats": each_cafe.seats,
            "has_toilet": each_cafe.has_toilet,
            "has_wifi": each_cafe.has_wifi,
            "has_sockets": each_cafe.has_sockets,
            "can_take_calls": each_cafe.can_take_calls,
            "coffee_price": each_cafe.coffee_price,
        })
    return jsonify(cafes=cafe_list)


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc").capitalize()
    result = db.session.execute(db.select(Cafe).where(Cafe.location==query_location))
    all_cafes = result.scalars().all()
    if all_cafes:
        cafe_list_location = []
        for cafe in all_cafes:
            cafe_list_location.append({"id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price}
            )
        return jsonify(cafes = cafe_list_location)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def post_new_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})
# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['GET', 'PATCH'])
def change_price(cafe_id):
    try:
        cafe = db.session.get(Cafe, cafe_id)
        if request.method == "PATCH":
            cafe.coffee_price = request.form.get("new_price")
            db.session.commit()
        return jsonify({"success": "Successfully updated the price"})
    except AttributeError:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404

# HTTP DELETE -  Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    cafe = db.session.get(Cafe, cafe_id)
    if not cafe:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
    key = request.form.get("api-key")
    if key != 'TopSecretAPIKey':
        return jsonify(error={"Unauthorized": "Invalid API key"})
    db.session.delete(cafe)
    db.session.commit()
    return jsonify(response={"Successful": "Cafe has been deleted"})


if __name__ == '__main__':
    app.run(debug=True)
