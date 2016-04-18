// index.js

exports.index = function (req, res) {
    res.render('index.ejs',
        {"title": "Hello world",
         "sites": {
             "zhihudaily": "知乎日报",
             "wenxuecity": "文学城",
             "jianshu": "简书",
             "ftchinese": "FT中文"
         }
        }
    );
}

exports.zhihudaily = function (req, res) {
    res.render('zhihudaily.ejs', {"title": "知乎日报"});
}
