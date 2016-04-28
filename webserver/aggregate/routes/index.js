var express = require('express');
var router = express.Router();
var homepage = require('models/home.js');
var site = require('models/site.js');

/* GET home page. */
router.get('/', homepage);

/* GET article list of a site. */
router.get('/:sitename', homepage);
router.get('/:sitename/:pageid', site.article);

module.exports = router;
