var express = require('express');
var router = express.Router();
var Sites = require('../models/sites');

/* GET home page. */
router.get('/', function(req, res, next) {
    debugger;
    sites = querySites(Sites);
    res.render('index', { title: 'Express' });
});

function querySites(SitesModel, res) {
    SitesModel.find(function(err, _sites, res) {
        var sites = {};
        for (var i=0; i<_sites.length; i++) {
            sites['name'] = _sites[i]['name'];
            sites['alias'] = _sites[i]['alias'];
        }
        console.log(sites);
        res.send(sites);
    });
}

module.exports = router;
