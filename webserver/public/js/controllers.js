var aggregate = angular.module('aggregate', []);

aggregate.controller('articlesCtrl', function($scope, $http){
    $scope.init = function(path) {
        console.log(path);
        $http.get(path).success(function(data) {
            console.log(data);
            $scope.sites = data.sites;
            $scope.articles = data.articles;
        });
    }
});
