
var DemoApp = angular.module('DemoApp', [
	'ngResource',
	'ngRoute'
]);
DemoApp.factory('DataResource', function($resource) {
	return $resource('/:datatype/:id/:file', {}, {
		query: {method: 'GET', isArray: true},
		get: {method: 'GET'},
		remove: {method: 'DELETE'},
		edit: {method: 'PUT'},
		set: {method: 'POST'}
	});
});
DemoApp.controller('DemoCtrl', function($scope, $routeParams, $location, DataResource, $route, $rootScope) {
	if (!$rootScope.authenticated) {
		DataResource.get({datatype:"me.cgi"}, function(data) {
			$rootScope.userdata = data;
			$rootScope.authenticated = true;
			DataResource.query({datatype:$rootScope.userdata.login, id:"repositories.json"}, function(repos) {
				$rootScope.repositories=repos;
			});
		}, function(error) {
			$rootScope.user = "";
			$rootScope.authenticated = false;
		});
	}
	if ($routeParams.username!=null && $routeParams.repo!=null) {
		$scope.username = $routeParams.username;
		$scope.repo = $routeParams.repo;
		$scope.item = DataResource.get({datatype:$routeParams.username, id:$routeParams.repo, file:"current.json"});
		if ($routeParams.action==null) {
			$routeParams.action="log";
		}
	}
	if ($routeParams.action!=null) {
		$scope.action = $routeParams.action;
	       	$scope.actiondata = DataResource.get({datatype:$routeParams.username, id:$routeParams.repo, file:$routeParams.action + ".json"});
	}
});
DemoApp.config(['$routeProvider', function($routeProvider) {
	$routeProvider
		.when('/:username/:repo/:action', {templateUrl: 'about.html', controller:'DemoCtrl'})
		.when('/:username/:repo', {templateUrl: 'about.html', controller: 'DemoCtrl'})
		.when('/', {templateUrl: 'home.html', controller: 'DemoCtrl'})
	;
}]);

DemoApp.filter('rawHtml', ['$sce', function($sce){
  return function(val) {
	json = JSON.stringify(val, undefined, 2);
	json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	something = json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
	} else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
	return '<span class="' + cls + '">' + match + '</span>';
    });

    return $sce.trustAsHtml(something);
  };
}]);
