[].forEach.call(document.querySelectorAll('a.marvel-issue'), function(el) {
  el.addEventListener('click', function() {
    var data = {
      comic: this.dataset.comic,
      issue: this.dataset.num,
      link: this.href
    };
    analytics.track('Read Comic', data);
  });
});
