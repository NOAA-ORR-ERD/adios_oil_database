export default function() {
  this.namespace = '/api';

  let oils = [{
    "name": "ALASKA NORTH SLOPE (NORTHERN PIPELINE, 1999)",
    "_id": "AD01988",
    "product_type": "crude",
    "location": "ALASKA, USA",
    "status": [],
    "categories": ["Crude-Medium"],
    "categories_str": "Medium",
    "pour_point": [218, 218],
    "apis": [
        {
            "gravity": 30.6,
            "weathering": 0,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        }
    ],
    "viscosity": 0.0000015019
  },
  {
    "name": "CASTOR OIL",
    "_id": "AD02062",
    "product_type": "refined",
    "location": null,
    "status": [
        "Imported Record has insufficient cut data"
    ],
    "categories": [],
    "categories_str": "",
    "pour_point": [251, 251],
    "apis": [
        {
            "gravity": 15.2,
            "weathering": 0,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        }
    ],
    "viscosity": 0.0002202149
  },
  {
    "name": "Cold Lake Winter Blend 2015",
    "_id": "EC002712",
    "product_type": "crude",
    "location": "Alberta, Canada",
    "status": [],
    "categories": ["Crude-Heavy"],
    "categories_str": "Heavy",
    "pour_point": [213.15, 213.15],
    "apis": [
        {
            "gravity": 21.9612697588,
            "weathering": 0,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 17.0938266782,
            "weathering": 0.0788,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 12.3589177879,
            "weathering": 0.1575,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 9.0413804427,
            "weathering": 0.2362,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        }
    ],
    "viscosity": 0.0000054105
  },
  {
    "name": "Alaska North Slope [2015]",
    "_id": "EC002713",
    "product_type": "crude",
    "location": "Alaska, USA",
    "status": [],
    "categories": ["Crude-Light"],
    "categories_str": "Light",
    "pour_point": [222.15, 222.15],
    "apis": [
        {
            "gravity": 31.32,
            "weathering": 0,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 25.3,
            "weathering": 0.1242,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 21.46,
            "weathering": 0.2456,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        },
        {
            "gravity": 17.93,
            "weathering": 0.3676,
            "_cls": "oil_database.models.oil.api.ApiGravity"
        }
    ],
    "viscosity": 0.0000061361
  }];

  this.get('/oils', function(db, request) {
    if(request.queryParams.name !== undefined) {
      let filteredOils = oils.filter(function(i) {
        return i.name.toLowerCase().indexOf(request.queryParams.name.toLowerCase()) !== -1;
      });
      return filteredOils;
    }
    else {
      return oils;
    }
  });

  // Find and return the provided oil from our oil list above
  this.get('/oils/:id', function (db, request) {
    return oils.find((oil) => request.params.id === oil._id);
  });

  this.passthrough('http://localhost:9898/**');
}
