var mongoose = require("mongoose");
var mongoosejs = require("./mongoose.js");
debugger;
var home = require("./home.js")

function homepage(req, res) {
    debugger;
    var sitename = req.params.sitename;
    var siteModel = mongoose.model(sitename, mongoosejs.articleSchema, sitename)

    siteModel.find(function(err, _articles) {
        debugger;
        var sitemap = {
            'zhihudaily': '知乎日报',
            'jianshu': '简书',
            'wenxuecity': '文学城'
        };
        var articles = [];
        for (var i=0; i<_articles.length; i++) {
            articles.push({
                'path': sitename + "/" + _articles[i]['pageid'],
                'title': _articles[i]['title'],
                'summary': _articles[i]['summary'],
            });
        }
        console.log(articles);
        res.render('sitehome',
            {
                'title': sitemap[sitename],
                'articles': articles
            }
        );
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
        res.render('article',
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
