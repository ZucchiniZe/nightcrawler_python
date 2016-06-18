Vue.http.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');

function getRun(start, end) {
  if (end === -1) return String(start);
  if (end === 0) return start + ' - Present';
  return start + ' - ' + end;
}

var app = new Vue({
  el: '#playlist-app',
  data: {
    id: window.data.id || 0,
    title: window.data.title || '',
    description: window.data.description || '',
    issues: window.data.items || [],
    creating: window.creating,
    iq: '',
    cq: '',
    searchResults: [],
    flashMessages: [],
    errors: null,
    requestNumber: 0
  },
  watch: {
    'iq': 'searchIssues',
    'cq': 'searchComics'
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
      this.flashMessages.push({type: type, text: text});

      setTimeout(function(){this.flashMessages.pop()}.bind(this), timeout)
    },
    searchIssues: function(term) {
      this.search(term, 'issue')
    },
    searchComics: function(term) {
      this.search(term, 'comic')
    },
    search: function(term, type) {
      // query /api/issue/search and get top 10 results
      var search = term.trim();
      if (search !== "") {
        var localRequestNumber = ++this.requestNumber;
        this.$http.get('/api/' + type + '/search/', {q: search}).then(function (response) {
          var data = response.data;
          if (this.requestNumber !== localRequestNumber) {
            console.log('stale request data');
            return
          }
          if (data.length > 0) {
            // elasticsearch returns text instead of title, lets change that
            this.searchResults = data.map(function (element) {
              // and lets add the run if the result is a comic
              element.run = element.type === 'comic' ? getRun(element.start, element.end) : false;
              element.title = element.text;
              delete element.text;
              return element
            }).slice(0, 10);
          } else {
            this.searchResults = [];
          }
        }.bind(this))
      } else {
        this.searchResults = []
      }
    },
    addResult: function(result) {
      if (result.type === 'issue') {
        this.addIssue(result)
      } else if (result.type === 'comic') {
        this.$http.get('/api/comic/' + result.id + '/issues/').then(function(response) {
          if (response.data.length > 0) {
            // if we have issues, lets add the id to them
            var issues = response.data.map(function(issue) {
              var extras = {id: issue.pk};
              for (var attr in extras) { issue.fields[attr] = extras[attr] }
              return issue.fields;
            });
            issues.map(function(issue) {
              this.addIssue(issue)
            }.bind(this))
          } else {
            this.flash('error', 'please sync this issue <a href="/comic/' + result.id + '/">here</a> before adding to playlist', 7000)
          }
        })
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
          if (window.creating) {
            this.flash('success', this.title + 'has been created redirecting now', 2000);
            this.errors = null;
            setTimeout(function() { window.location.replace('/playlist/' + res.data.id) }, 2000)
          } else {
            this.flash('success', this.title + ' has been updated', 2000);
            this.errors = null;
          }
        } else {
          this.flash('error', 'something went wrong, look below', 2000);
          this.errors = res.data.errors;
          console.log(res.data)
        }
      });
    }
  }
});
