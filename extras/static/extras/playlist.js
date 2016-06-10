Vue.http.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');
// Vue.http.options.emulateJSON = true;

var app = new Vue({
  el: '#playlist-app',
  data: {
    title: window.data.title || '',
    description: window.data.description || '',
    issues: window.data.items || [],
    q: '',
    searchResults: []
  },
  watch: {
    'q': 'search'
  },
  computed: {
    ids: function() {
      return this.issues.map(function(issue) {
        return issue.id
      })
    }
  },
  methods: {
    search: function(term) {
      var search = term.trim();
      if (search !== "") {
        this.$http.get('/api/issue/search', {q: search}).then(function (response) {
          var data = response.data;
          if (data.length > 0) {
            // elasticsearch returns text instead of title, lets change that
            this.searchResults = data.map(function (element) {
              element.title = element.text;
              delete element.text;
              return element
            });
          } else {
            this.searchResults = [];
          }
        }.bind(this))
      } else {
        this.searchResults = []
      }
    },
    addIssue: function(newIssue) {
      var exists = false;
      this.issues.map(function(issue) {
        if (issue.id === newIssue.id) {
          exists = true;
        }
      }.bind(this));
      if (!exists) {
        this.issues.push(newIssue);
      }
    },
    removeIssue: function(index) {
      this.issues.splice(index, 1)
    },
    sendForm: function() {
      this.$http({
        url: '{?title,description,items*}',
        method: 'post',
        data: {
          title: this.title,
          description: this.description,
          items: this.ids
        }
      });
    }
  }
});

/*
  django form uses post request with regular named params
  example params
  ?title=a%2Bx&description=a%2Bx+reading+order&items=27911&items=28150&items=31720&items=576
  items is repeated as many times there are issues with the issue's id
 */
