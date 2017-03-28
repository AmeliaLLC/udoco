module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    concat: {
      app: {
        src: [
          'static/application/*.js',
        ],
        dest: 'static/app.js',
      },
      style: {
        src: [
          'static/application/*.css',
        ],
        dest: 'static/app.css'
      }
    },

    uglify: {
      app: {
        files: {'static/app.min.js': ['static/app.js']},
      }
    },

    watch: {
      options: {livereload: true},
      javascript: {
          files: ['static/application/**/*.js'],
        tasks: ['concat']
      }
    }
  });

  // Load plugins here.
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Register tasks here.
  grunt.registerTask('default', []);
};
