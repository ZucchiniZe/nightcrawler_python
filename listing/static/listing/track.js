[].forEach.call(document.querySelectorAll('a.read-link'), function(el) {
  el.addEventListener('click', function() {
    var data = {
      comic: this.dataset.comic,
      issue: this.dataset.num,
      link: this.href
    };
    analytics.track('Read Comic', data);
  });
});