var mongoose = require("mongoose");
mongoose.connect('mongodb://localhost/mass')
var db = mongoose.connection;

db.on('error', console.error);
var siteSchema = mongoose.Schema({
    'name': String,
    'alias': String,
});
var Sites = mongoose.model('fetched_webs', siteSchema);

module.exports = Sites;
