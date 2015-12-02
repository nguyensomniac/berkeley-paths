var path = require('path');

var gulp = require('gulp');

var sass = require('gulp-sass');
var cssMin = require('gulp-minify-css');

var jsMin = require('gulp-uglify');

var concat = require('gulp-concat');
var filter = require('gulp-filter');
var bowerFiles = require('main-bower-files');

var input = {
  sass: {
    main: path.join(__dirname, 'app', 'src', 'css', 'main.scss'),
    all: path.join(__dirname, 'app', 'src', 'css', '**')
  },
  bower: path.join(__dirname, 'bower_components'),
  js: path.join(__dirname, 'app', 'src', 'js', '**')
};

var output = {
  css: path.join(__dirname, 'app', 'static'),
  js: path.join(__dirname, 'app', 'static')
};

gulp.task('css', function() {
  var files = bowerFiles();
  files.push(input.sass.main);
  var cssFilter = filter([path.join('**', '*.scss'), path.join('**', '*.css')]);
  gulp.src(files)
    .pipe(cssFilter)
    .pipe(sass())
    .pipe(concat('all.css'))
    .pipe(cssMin())
    .pipe(gulp.dest(output.css));
});

gulp.task('js', function()  {
  gulp.src(input.js)
    .pipe(concat('app.js'))
    .pipe(jsMin())
    .pipe(gulp.dest(output.js));
})

gulp.task('vendor', function()  {
  var files = bowerFiles()
  var jsFilter = filter([path.join('**', '*.js')], {restore: true});
  // var mapboxFilter = filter(path.join('**', 'mapbox.js'));
  gulp.src(files)
    .pipe(jsFilter)
    .pipe(jsMin())
    .pipe(concat('vendor.js'))
    .pipe(gulp.dest(output.js));
})

gulp.task('watch', function() {
  gulp.watch(input.sass.all, ['css']);
  gulp.watch(input.js, ['js']);
});

gulp.task('build', ['css', 'js', 'vendor']);