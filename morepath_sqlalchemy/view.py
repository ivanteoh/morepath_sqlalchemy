from .model import Document, Root
from .main import app, Session
from .collection import DocumentCollection
from morepath import redirect
from webob.exc import HTTPNotFound


@app.json(model=Root)
def root_default(self, request):
    return redirect('/documents')


@app.json(model=Document)
def document_default(self, request):
    return {'id': self.id,
            'title': self.title,
            'content': self.content,
            'link': request.link(self)}


@app.json(model=DocumentCollection)
def document_collection_default(self, request):
    return {
        'documents': [request.view(doc) for doc in self.query()],
        'previous': request.link(self.previous(), default=None),
        'next': request.link(self.next(), default=None),
        'add': request.link(self, 'add'),
        }


@app.html(model=DocumentCollection, name='add')
def document_collection_add(self, request):
    return '''\
<html>
<body>
<form action="/documents/add_submit" method="POST">
title: <input type="text" name="title"><br>
content: <input type="text" name="content"><br>
<input type="submit" value="Add!"><br>
</form>
</body>
</html>
'''


@app.html(model=DocumentCollection, name='add_submit', request_method='POST')
def document_collection_add_submit(self, request):
    title = request.POST.get('title')
    content = request.POST.get('content')
    document = self.add(title=title, content=content)
    return "<p>Awesome %s</p>" % document.id


@app.html(model=Document, name='edit', request_method='GET')
def document_edit_get(self, request):
    return '''\
<html>
<body>
<form action="/documents/%s/edit" method="POST">
title: <input type="text" name="title" value="%s"><br>
content: <input type="text" name="content" value="%s"><br>
<input type="submit" value="Update!"><br>
</form>
</body>
</html>
''' % (str(self.id), self.title, self.content)


@app.html(model=Document, name='edit', request_method='POST')
def document_edit_post(self, request):
    session = Session()
    self.title = request.POST.get('title')
    self.content = request.POST.get('content')
    session.add(self)
    session.flush()
    return "<p>post edit view on model: %s</p>" % self.id


@app.html(model=HTTPNotFound, name='error')
def notfound_custom(self, request):
    def set_status_code(response):
        response.status_code = 404  # pass along 404
    request.after(set_status_code)
    return "<p>My document not found!</p>"
