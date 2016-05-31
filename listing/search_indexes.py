from haystack import indexes

from .models import Comic, Issue


class ComicIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')
    scraped = indexes.BooleanField(model_attr='scraped')
    start = indexes.IntegerField(model_attr='start')
    end = indexes.IntegerField(model_attr='end')
    type = indexes.CharField(default='comic')

    def get_model(self):
        return Comic


class IssueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')
    num = indexes.IntegerField(model_attr='num')
    type = indexes.CharField(default='issue')

    def get_model(self):
        return Issue