var mongoose = require("./mongoose.js");

function homepage(req, res) {
    mongoose.sitemapModel.find(function(err, _sites) {
        var sites = [];
        for (var i=0; i<_sites.length; i++) {
            sites.push({
                'name': _sites[i]['name'],
                'alias': _sites[i]['alias']
            });
        }
        console.log(sites);
        res.render('index',
            {
                title: 'Aggeregate',
                'sites': sites
            }
        );
    });
}

module.exports = homepage;
