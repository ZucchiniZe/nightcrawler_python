Array.prototype.move = function(from,to){
  this.splice(to,0,this.splice(from,1)[0]);
  return this;
};

var issues = [{"num": 3, "type": "issue", "text": "A+X #3", "id": 28270}, {"num": 11, "type": "issue", "text": "A+X #11", "id": 30954}, {"num": 17, "type": "issue", "text": "A+X #17", "id": 33033}, {"num": 1, "type": "issue", "text": "Wolverine #1", "id": 576}, {"num": 5, "type": "issue", "text": "A+X #5", "id": 28566}, {"num": 8, "type": "issue", "text": "A+X #8", "id": 29928}, {"num": 1, "type": "issue", "text": "A+X #1", "id": 27911}, {"num": 2, "type": "issue", "text": "A+X #2", "id": 28150}, {"num": 4, "type": "issue", "text": "A+X #4", "id": 28456}, {"num": 7, "type": "issue", "text": "A+X #7", "id": 29122}, {"num": 12, "type": "issue", "text": "A+X #12", "id": 31508}, {"num": 13, "type": "issue", "text": "A+X #13", "id": 31720}, {"num": 14, "type": "issue", "text": "A+X #14", "id": 31964}, {"num": 16, "type": "issue", "text": "A+X #16", "id": 32789}, {"num": 18, "type": "issue", "text": "A+X #18", "id": 33474}, {"num": 2, "type": "issue", "text": "Wolverine #2", "id": 3637}, {"num": 3, "type": "issue", "text": "Wolverine #3", "id": 3640}, {"num": 4, "type": "issue", "text": "Wolverine #4", "id": 3643}, {"num": 6, "type": "issue", "text": "A+X #6", "id": 29131}, {"num": 9, "type": "issue", "text": "A+X #9", "id": 30238}, {"num": 10, "type": "issue", "text": "A+X #10", "id": 30653}, {"num": 15, "type": "issue", "text": "A+X #15", "id": 32446}]

var app = new Vue({
  el: '#playlist-app',
  data: {
    q: '',
    issues: [],
    searchResults: issues
  },
  watch: {
    'q': 'search'
  },
  methods: {
    search: function(term) {
      var search = term.trim();
      $.ajax({
        url: '/api/issue/search',
        type: 'get',
        data: {
          q: search
        }
      }).done(function (data) {
        if (data.length > 0) {
          this.searchResults = data;
        } else {
          this.searchResults = [];
        }
      }.bind(this))
    },
    addIssue: function(issue) {
      console.log('added', issue.id);
      this.issues.push(issue)
    },
    removeIssue: function(index) {
      this.issues.splice(index, 1)
    },
    moveIssueUp: function(index) {
      this.issues.move(index, index-1);
    },
    moveIssueDown: function(index) {
      this.issues.move(index, index+1);
    }
  }
});
