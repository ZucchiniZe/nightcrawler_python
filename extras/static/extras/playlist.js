Vue.http.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');

var app = new Vue({
  el: '#playlist-app',
  data: {
    title: window.data.title || '',
    description: window.data.description || '',
    issues: window.data.items || [],
    q: '',
    searchResults: [],
    messages: []
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
    flash: function(type, text, timeout) {
      this.messages.push({type: type, text: text});
      setTimeout(function(){this.messages.pop()}.bind(this), timeout)
    },
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
      this.$http.post('.', {
        title: this.title,
        description: this.description,
        items: this.ids
      }).then(function(res) {
        if (res.data.success) {
          this.flash('success', this.title + ' has been updated', 2000);
        } else {
          this.flash('error', 'something went wrong', 2000);
          console.log(res.data.errors)
        }
      });
    }
  }
});
