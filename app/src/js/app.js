var app = angular.module('paths', ['ui.router']);

// Get public config vars from server
app.service('appConfig', function($http) {
  var promise;
  this.getConfig = function() {
    if (!promise) {
      promise = $http.get('/config').then(function(res) {
        return res.data;
      })
    }
    return promise;
  }
});

app.config(function($stateProvider, $urlRouterProvider, $locationProvider)  {
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: '/static/partials/home-partial.html'  
    })
    .state('home.participate',   {
      url: 'participate',
      abstract: true,
      template: '<survey></survey>'
    })
    .state('home.participate.download', {
      url: '',
      templateUrl: '/static/partials/survey-one.html'
    })
    .state('home.participate.connect', {
      url: 'participate/connect',
      templateUrl: '/static/partials/survey-two.html'
    })
    .state('home.participate.survey', {
      url: 'participate/survey',
      templateUrl: '/static/partials/survey-three.html'
    })
    .state('home.participate.finished', {
      url: 'participate/complete',
      templateUrl: '/static/partials/survey-four.html'
    })
  $locationProvider.html5Mode(true);
});

app.directive('survey', function()  {
  return  {
    templateUrl: '/static/partials/survey-wrapper.html'
  }
})

app.controller('MainCtrl', function(appConfig, $scope)  {
  appConfig.getConfig().then(function(config)  {
    $scope.config = config;
    $scope.formData = {};
    // $scope.processForm  
  })
})
