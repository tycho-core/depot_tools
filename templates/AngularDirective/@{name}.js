@require(name)
@include("cpp_copyright_comment")
'use strict';

angular.module('@{name}', [])
    .directive('@{name}', ['$sce', 'fadAPIService', 
        function ($sce, fadAPIService) {
            return {
                require: '',
                restrict: 'A',
                scope: {
                },
                controller: ['$scope', function ($scope) {
                }],
                link: function (scope, element, attrs) {
                },
                templateUrl: $sce.trustAsResourceUrl(
                    resolve_static_url('js/directives/@{name}/@{name}.html'))
            };
        }]);
