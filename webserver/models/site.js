var mongoose = require("mongoose");
var mongoosejs = require("models/mongoose.js");
var home = require("models/home.js")

function homepage(req, res) {
    var sitename = req.params.sitename;
    var siteModel = mongoose.model(sitename, mongoosejs.articleSchema, sitename);

    mongoosejs.sitemapModel.find(function(err, _sites) {
        var sites = [];
        for (var i=0; i<_sites.length; i++) {
            sites.push({
                'name': _sites[i]['name'],
                'alias': _sites[i]['alias']
            });
        }
    
        siteModel.find(function(err, _articles) {
            var articles = [];
            for (var i=0; i<_articles.length; i++) {
                articles.push({
                    'pageid': _articles[i].pageid,
                    'path': sitename + "/" + _articles[i]['pageid'],
                    'title': _articles[i]['title'],
                    'content': _articles[i]['content'],
                    'image': _articles[i]['image'],
                });
            }
            res.json(
                {
                    'sites': sites,
                    'articles': articles
                }
            );
        });
    });
}

function article(req, res) {
    sitename = req.params.sitename;
    pageid = req.params.pageid;
    siteModel = mongoose.model(sitename, mongoosejs.articleSchema, sitename)

    siteModel.find({'pageid': pageid}, function(err, _articles) {
        if (_articles.length > 1) {
            throw "Find multiple articles";
        }
        if (_articles.length > 0) {
            article = _articles[0];
            console.log(_articles)
            console.log("article is " + article);
            res.json(
                {
                    'title': article.title,
                    'content': article.content
                }
            );
        } else {
            res.send("Not found");
        }
    });
}

module.exports = {
    homepage: homepage,
    article: article
}
