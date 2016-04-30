var aggregate = angular.module('aggregate', []);

aggregate.controller('articlesCtrl', function($scope, $http, $sce){
    $scope.go = function(path) {
        console.log(path);
        $http.get(path).success(function(data) {
            console.log(data);
            $scope.sites = data.sites;
            $scope.articles = data.articles;
            $scope.showlist = true;
            $scope.showcontent = false;
        });
    }
    $scope.read = function(path) {
        console.log(path);
        $http.get(path).success(function(data) {
            console.log(data);
            $scope.article = data;
            $scope.showlist = false;
            $scope.showcontent = true;
            $scope.article.content = $sce.trustAsHtml(data.content);
        });
    }
});
