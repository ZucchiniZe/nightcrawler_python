var app = new Vue({
  el: '#playlist-app',
  data: {
    q: '',
    issues: window.items,
    searchResults: []
  },
  watch: {
    'q': 'search'
  },
  methods: {
    search: function(term) {
      var search = term.trim();
      if (search !== "") {
        $.ajax({
          url: '/api/issue/search',
          type: 'get',
          data: {
            q: search
          }
        }).done(function (data) {
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
    addIssue: function(issue) {
      this.issues.push(issue)
    },
    removeIssue: function(index) {
      this.issues.splice(index, 1)
    }
  }
});

/*
  django form uses post request with regular named params
  example params
  ?title=a%2Bx&description=a%2Bx+reading+order&items=27911&items=28150&items=31720&items=576
  items is repeated as many times there are issues with the issue's id
 */
