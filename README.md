# sxml (simple lxml)
Содержить функции для упрощения работы с lxml.
Позволяет выстроить эти функции в пайплайн обработки xml/html документы
(что-то типа "программирование на yaml")
Не предназначена для работы с большими xml файлами.
для примеров использования см tests

# TODO:
* add throttler
* add method breakpoint
* add method date.parse
* add method file.read
* add method sxml.cms.common.table/dl/ul
* validate if $chain contains list
* validate empty config
* precieding text
* include most common ns for xpath (re, date, ...):
  - http://exslt.org/
  - https://stackoverflow.com/questions/26951061/lxml-find-tags-by-regex
* add imports other libraries
* add methods from urllib (urlparse, parse_qs)
* fix indentation in prettify
* how can i get image url from css?
* query None == self|copy/raw
* add selectors for most common cms (wp, ...)
* add methods for sitemap parsing
* add methods for robots.txt parsing
* add methods xml.loads xml.dumps (with remove or autoload ns):
  - https://stackoverflow.com/questions/18159221/remove-namespace-and-prefix-from-xml-in-python-using-lxml
  - https://stackoverflow.com/questions/4210730/how-do-i-use-xml-namespaces-with-find-findall-in-lxml
* add function for xml to json
* add test for base_url resolve <a href="tel:+79999999999">tel</a>
* add test for wiktionary: hello and punctuation
