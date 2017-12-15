function IndexCtrl($scope) {
    $log.log('index');
}

function SearchCtrl($scope, $log, $http) {
    $scope.word = '';
    $scope.searchWord = function () {
        $log.log($scope.word);
        var word = $scope.word;
        $http({
            method: 'GET',
            url: '/search',
            params: {word: word}
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            $log.log(response);
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            $log.log(response);
        });
    };

}