var mongoose = require("mongoose");
var mongoosejs = require("models/mongoose.js");
var home = require("models/home.js")

function homepage(req, res) {
    debugger;
    var sitename = req.params.sitename;
    var siteModel = mongoose.model(sitename, mongoosejs.articleSchema, sitename);

    mongoosejs.sitemapModel.find(function(err, _sites) {
        var sitemap = {};
        for (var i=0; i<_sites.length; i++) {
            sitemap[_sites[i]['name']] = _sites[i]['alias'];
        }
    
        siteModel.find(function(err, _articles) {
            debugger;
            var articles = [];
            for (var i=0; i<_articles.length; i++) {
                articles.push({
                    'path': sitename + "/" + _articles[i]['pageid'],
                    'title': _articles[i]['title'],
                    'summary': _articles[i]['summary'],
                });
            }
            res.render('sitehome',
                {
                    'title': sitemap[sitename],
                    'articles': articles
                }
            );
        });
    });
}

function article(req, res) {
    debugger;
    sitename = req.params.sitename;
    pageid = req.params.pageid;
    siteModel = mongoose.model(sitename, mongoosejs.articleSchema, sitename)

    siteModel.find({'pageid': pageid}, function(err, _articles) {
        debugger;
        if (_articles.length > 1) {
            throw "Find multiple articles";
        }
        article = _articles[0];
        debugger;
        console.log("article is " + article);
        res.render('index',
            {
                'title': article['title'],
                'content': article['content']
            }
        );
    });
}

module.exports = {
    homepage: homepage,
    article: article
}
