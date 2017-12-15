'use strict';

angular.module('googleforadayApp', ['ngRoute'])
    .config(['$routeProvider', '$locationProvider',
        function ($routeProvider, $locationProvider) {
            $routeProvider
                .when('/', {
                    templateUrl: 'partials/index.html',
                    controller: IndexCtrl
                })
                .when('/search', {
                    templateUrl: 'partials/search.html',
                    controller: SearchCtrl
                })
                .otherwise({
                    redirectTo: '/'
                });
            $locationProvider.hashPrefix('');
        }]);