[].forEach.call(document.querySelectorAll('a.read-issue'), function(el) {
  el.addEventListener('click', function(e) {
    // e.preventDefault();
    
    var data = {
      comic: this.dataset.comic,
      issue: this.dataset.num,
      link: this.href
    };
    analytics.track('Read Comic', data);

    var url = encodeURI('/read/issue/'+this.dataset.comicid+'/'+this.dataset.issueid+'/');
      
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.send();
  });
});