var mongoose = require("mongoose");
mongoose.connect('mongodb://localhost/mass')
var db = mongoose.connection;
db.on('error', console.error);

var sitemapSchema = mongoose.Schema({
    'name': String,
    'alias': String,
});
var sitemapModel = mongoose.model('fetched_webs', sitemapSchema, 'fetched_webs');


var articleSchema = mongoose.Schema({
    'pageid': String,
    'title': String,
    'timestamp': String,
    'summary': String,
    'content': String,
    'content-title': String,
    'page': String
});


module.exports = {
    mongoose: mongoose,
    db: db,
    sitemapSchema: sitemapSchema,
    sitemapModel: sitemapModel,
    articleSchema: articleSchema,
};
