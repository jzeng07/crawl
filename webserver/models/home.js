var mongoose = require("mongoose");
var mongoosejs = require("models/mongoose.js");

function homepage(req, res) {
    var sitename = req.params.sitename;
    var pageid = req.params.pageid;

    mongoosejs.sitemapModel.find(function(err, _sites) {
        var sites = [];
        for (var i=0; i<_sites.length; i++) {
            sites.push({
                'name': _sites[i]['name'],
                'alias': _sites[i]['alias']
            });
        }

        console.log(sites);
        var active_site = sites[0]['name'];
        if (sitename != undefined) {
            active_site = sitename;
        }

        var siteModel = mongoose.model(active_site, mongoosejs.articleSchema, active_site);
        siteModel.find(function(err, _articles) {
            var articles = [];
            for (var i=0; i<_articles.length; i++) {
                articles.push({
                    'path': active_site + "/" + _articles[i]['pageid'],
                    'title': _articles[i]['title'],
                    'summary': _articles[i]['summary'],
                });
            }

            if (pageid === undefined) {
                res.render('index',
                    {
                        'title': 'Aggeregate',
                        'sites': sites,
                        'articles': articles,
                        'active_site': active_site,
                        'content': ""
                    }
                );
            } else {
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
                            'sites': sites,
                            'articles': articles,
                            'active_site': active_site,
                            'content': article['content']
                        }
                    );
                });
            }

        });
    });
}

module.exports = homepage;
