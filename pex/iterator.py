# Copyright 2015 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

"""The glue between fetchers, crawlers and requirements."""

from __future__ import absolute_import

import itertools
from abc import abstractmethod

from pex.compatibility import AbstractClass
from pex.crawler import Crawler
from pex.fetcher import PyPIFetcher
from pex.package import Package


class IteratorInterface(AbstractClass):
  @abstractmethod
  def iter(self, req):
    """Return a list of packages that satisfy the requirement."""
    pass


class Iterator(IteratorInterface):
  """A requirement iterator, the glue between fetchers, crawlers and requirements."""

  def __init__(self, fetchers=None, crawler=None, follow_links=False, allow_prereleases=None):
    self._crawler = crawler or Crawler()
    self._fetchers = fetchers if fetchers is not None else [PyPIFetcher()]
    self.__follow_links = follow_links
    self.__allow_prereleases = allow_prereleases

  def _iter_requirement_urls(self, req):
    return itertools.chain.from_iterable(fetcher.urls(req) for fetcher in self._fetchers)

  def iter(self, req):
    url_iterator = self._iter_requirement_urls(req)
    crawled_url_iterator = self._crawler.crawl(url_iterator, follow_links=self.__follow_links)
    for package in filter(None, map(Package.from_href, crawled_url_iterator)):
      if package.satisfies(req, allow_prereleases=self.__allow_prereleases):
        yield package
