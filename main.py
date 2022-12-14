import fileapp
import flask
import logging
import urllib

from google.cloud import storage
from fileobjects import DisplayInfo
from fileobjects import UploadedFile


app = flask.Flask(__name__)

_BUCKET_NAME = 'test-to-learn-image-uploads'

@app.route('/')
def root():
    di = DisplayInfo('File Upload')
    return flask.render_template('index.html', di)

@app.route('/upload', methods=['POST'])
def upload():
    di = DisplayInfo('File Upload')
    uploaded_file = flask.request.files.get('file')

    if not uploaded_file:
        di.add_error('No file uploaded.')

    filename = flask.request.form.get('filename')

    if not filename:
        di.add_error('No file name provided.')

    if di.errors:
        return flask.render_template('index.html', di)

    gcs_client = storage.Client()
    storage_bucket = gcs_client.get_bucket(_BUCKET_NAME)
    blob = storage_bucket.blob(uploaded_file.filename)

    c_type = uploaded_file.content_type
    blob.upload_from_string(uploaded_file.read(), content_type=c_type)

    fileapp.save_file(filename, blob.public_url)

    return flask.redirect('/showfile?name=' + urllib.parse.quote_plus(filename))


@app.route('/showfile')
def showfile():
    filename = flask.request.args['name']
    di = fileapp.get_uploaded_file_display(filename)
    return flask.render_template('showfile.html', di)
