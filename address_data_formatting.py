import pandas as pd
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ

# this file i included just to show the script i run locally to create a database to use with the live api
# this is what i will run with the new xcel sheet from the city of denver open data project

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'sqlite:///addresses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#
denver_data = pd.read_excel("properties.xlsx")
denver_properties = denver_data.to_dict('records')

# need a method to loop over these, grab the address, query the database for that address,
# then add the latitude and longitudes to that property entry
location_data = pd.read_excel("addresslocations.xlsx")
locations = location_data.to_dict('records')


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


db.create_all()


def check_if_float(number):
    if type(number) == float:
        return str(int(number))
    else:
        return number


def make_list_items_strings(list_object):
    new_list = []
    for obj in list_object:
        if obj is None:
            obj = ""
            new_list.append(obj)
        elif pd.isna(obj):
            obj = ""
            new_list.append(obj)
        elif type(obj) == float:
            new_list.append(str(int(obj)))
        else:
            new_list.append(obj)
    return " ".join(new_list)


def load_locations_into_db(locations_xl):
    for location in locations_xl:
        prop = Address.query.filter_by(site_address=location['address']).first()
        if prop is None:
            continue
        else:
            prop.site_long = location['longitude']
            prop.site_lat = location['lattitude']
    db.session.commit()


def load_denver_xl_into_db(properties):
    for property_entry in properties:

        for key in property_entry:
            if property_entry[key] is None:
                property_entry[key] = ""
            elif pd.isna(property_entry[key]):
                property_entry[key] = ""

        owner_number = check_if_float(property_entry['OWNER_NUM'])
        owner_address = make_list_items_strings([owner_number,
                                                 property_entry['OWNER_DIR'],
                                                 property_entry['OWNER_TYPE'],
                                                 property_entry['OWNER_APT'],
                                                 property_entry['OWNER_CITY'],
                                                 property_entry['OWNER_STATE'],
                                                 property_entry['OWNER_ZIP'],
                                                 ])
        site_number = check_if_float(property_entry['SITE_NBR'])
        site_address = make_list_items_strings([site_number,
                                                property_entry['SITE_DIR'],
                                                property_entry['SITE_NAME'],
                                                property_entry['SITE_MODE'],
                                                ])

        address = Address(owner=property_entry['OWNER'],
                          co_owner=property_entry['CO_OWNER'],
                          owner_address=owner_address,
                          site_address=site_address,
                          site_more=property_entry['SITE_MORE'],
                          land_value=property_entry['ASMT_APPR_LAND'],
                          total_value=property_entry['TOTAL_VALUE'],
                          assess_value=property_entry['ASSESS_VALUE'],
                          taxable_value=property_entry['ASMT_TAXABLE'],
                          taxes_exempt=property_entry['ASMT_EXEMPT_AMT'],
                          property_class_desc=property_entry['PROPERTY_CLASS_DESC'],
                          bld_name=property_entry['BLD_NAME'],
                          zoning=property_entry['ZONE10'],
                          d_class_cn=property_entry['D_CLASS_CN'],
                          neighborhood=property_entry['NBHD_1_CN'],
                          year_built=property_entry['ORIG_YOC'] # for this line look at running check if float to strip the number of its .0
                          )
        db.session.add(address)
    db.session.commit()


# run the below to load the new denver data into a new database
# load_denver_xl_into_db(denver_properties)
# load_locations_into_db(locations)


@app.route('/')
def home():
    return "<p>Land Peasants Unite</p>"


@app.route('/all')
def get_all():
    addresses = db.session.query(Address).all()
    return jsonify(addresses=[address.to_dict() for address in addresses])


if __name__ == "__main__":
    app.run(debug=True)
