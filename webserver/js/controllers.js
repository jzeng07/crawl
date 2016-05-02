var aggregate = angular.module('aggregate', []);

aggregate.controller('articlesCtrl', function($scopt, $http){
    $http.get('/wenxuecity').success(function(data) {
        console.log(data);
        $scope.articles = data;
    });
});
