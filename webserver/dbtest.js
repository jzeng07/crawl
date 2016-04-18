var mongo = require('mongodb');

server = new mongo.Server("localhost", 27017, {auto_reconnect: true});
db = new mongo.Db("mass", server);

db.open(function(err, db) {
    if (!err) {
        db.collection("wenxuecity", function(err, collection) {
            console.log(collection);
            collection.find({"timestamp": {$gt: "2016-04-16"}}).toArray(function(err, bars) {
                if (!err) {
                    console.log(bars);
                } else {
                    console.log(err);
                }
            });
        });
    }
});

