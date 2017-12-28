function IndexCtrl($scope, $log, $http) {
    $scope.index = {
        done: false,
        nw: 0,
        nl: 0,
        waiting: false,
        url: ''
    };
    $scope.clear = {
        done: false,
        waiting: false
    };

    $scope.indexURL = function () {
        $log.log($scope.index.url);
        var url = $scope.index.url;
        $scope.index.waiting = true;
        $scope.index.done = false;
        $scope.clear.done = false;
        $http({
            method: 'POST',
            url: '/index-url',
            params: {url: url}
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            $log.log(response);
            $scope.index.nw = response.data.nw || 0;
            $scope.index.nl = response.data.nl || 0;
            $scope.index.waiting = false;
            $scope.index.done = true;
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            $log.log(response);
            $scope.index.waiting = false;
            $scope.index.done = false;
        });
    };
    $scope.clearIndex = function () {
        $scope.clear.done = false;
        $scope.clear.waiting = true;
        $scope.index.done = false;
        $http({
            method: 'POST',
            url: '/clear-index'
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            $log.log(response);
            $scope.clear.waiting = false;
            $scope.clear.done = true;
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            $log.log(response);
            $scope.clear.waiting = false;
            $scope.clear.done = false;
        });
    };
}

function SearchCtrl($scope, $log, $http) {
    $log.log('search');
    $scope.result = [];
    $scope.search = {
        done: false,
        word: '',
        result: [],
        waiting: false
    };
    $scope.searchWord = function () {
        $log.log($scope.search.word);
        $scope.search.waiting = true;
        var word = $scope.search.word;
        $http({
            method: 'GET',
            url: '/search-word',
            params: {word: word}
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            $log.log(response);
            $scope.result = response.data.result;
            $scope.search.waiting = false;
            $scope.search.done = true;
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            $log.log(response);
            $scope.search.waiting = false;
        });
    };

}