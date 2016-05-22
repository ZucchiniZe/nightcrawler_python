$('a.marvel-issue').click(function(e) {
    var data = {
        comic: this.dataset.comic,
        issue: this.dataset.num,
        link: this.href
    }
    analytics.track('Read Comic', data)
})
