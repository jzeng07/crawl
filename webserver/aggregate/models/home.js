var mongoose = require("mongoose");
var mongoosejs = require("models/mongoose.js");

function homepage(req, res) {
    var sitename = req.params.sitename;

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
 
            res.render('index',
                {
                    title: 'Aggeregate',
                    'sites': sites,
                    'articles': articles,
                    'active_site': active_site
                }
            );
        });
    });
}

module.exports = homepage;
