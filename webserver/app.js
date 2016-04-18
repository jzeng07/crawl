// index.js

var express = require('express');
var app = express();
var path = require('path');
var http = require('http');
var routes = require("./routes");

// all environments
app.set('port', process.env.PORT || 3000);
app.set("views", path.join(__dirname, "views"));
app.set("view engin", "ejs");
//app.use(express.logger('dev'));
//app.use(express.json());
//app.use(express.urlencoded());
//app.use(express.methodOverride());
//app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// development only
//if ('development' == app.get('env')) {
//    app.use(express.errorHandler());
//}

app.get('/', routes.index);
app.get('/zhihudaily', routes.zhihudaily);

http.createServer(app).listen(app.get('port'), function() {
    console.log('Express server listening on port ' + app.get('port'));
});
