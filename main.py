from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
# for local
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'sqlite:///Data/addresses.db')
# for deployed
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Address(db.Model):
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(100), nullable=True)
    co_owner = db.Column(db.String(100), nullable=True)
    owner_address = db.Column(db.String(1000))
    site_address = db.Column(db.String(1000))
    site_more = db.Column(db.String(100))
    site_long = db.Column(db.String(100))
    site_lat = db.Column(db.String(100))
    land_value = db.Column(db.String(50))
    total_value = db.Column(db.String(100))
    assess_value = db.Column(db.String(50))
    taxable_value = db.Column(db.String(100))
    taxes_exempt = db.Column(db.String(100))
    property_class_desc = db.Column(db.String(100))
    bld_name = db.Column(db.String(100))
    zoning = db.Column(db.String(100))
    d_class_cn = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    year_built = db.Column(db.String(100))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def print_all_neighborhoods(addresses):
    nh_set = {addy.neighborhood for addy in addresses}
    nh_list = list(nh_set)
    nh_list.sort()
    for nh in nh_list:
        print(nh)


@app.route('/all')
def get_all():
    addresses = db.session.query(Address).all()
    # print_all_neighborhoods(addresses)
    return jsonify(addresses=[address.to_dict() for address in addresses])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search_all_owned")
def get_all_owned_properties():
    query_address = request.args.get('address')
    address = db.session.query(Address).filter_by(site_address=query_address).first()
    if address:
        all_owned = db.session.query(Address).filter_by(owner_address=address.owner_address).all()
        if all_owned:
            return jsonify(owned=[addy.to_dict() for addy in all_owned])
        else:
            return jsonify(error={'not found': "Sorry no records for that query"})
    else:
        return jsonify(error={'not found': "Sorry no records for that query"})


@app.route("/search_neighborhood")
def get_all_neighborhood_properties():
    nh_request = request.args.get('neighborhood')
    if nh_request:
        all_neighborhood = db.session.query(Address).filter_by(neighborhood=nh_request).all()
        if all_neighborhood:
            return jsonify(neighborhood=[addy.to_dict() for addy in all_neighborhood])
        else:
            return jsonify(error={'not found': "Sorry no records for that query"})
    else:
        return jsonify(error={'not found': "Sorry no records for that query"})


if __name__ == "__main__":
    app.run()
